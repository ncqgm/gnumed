-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- for some strange reason log tables in old database may (already/still)
-- carry .row_version / .modified_by / .modified_when
drop function if exists staging.drop_legacy_log_columns() cascade;

create function staging.drop_legacy_log_columns()
	returns void
	language plpgsql
	as '
DECLARE
	__cols2drop name[];
	__col2drop name;
	__SQL text;
	__SQL__get_log_tables text;
	__audit_table__name text;
	__audit_table__table_oid oid;
BEGIN
	RAISE NOTICE ''dropping legacy columns from log tables'';
	__cols2drop := ARRAY[''row_version'',''modified_by'',''modified_when''];
	RAISE NOTICE ''%'', __cols2drop;
	__SQL__get_log_tables := format (''
		select
			pg_cl.relname, pg_cl.oid
		from
			pg_namespace pg_ns, pg_class pg_cl
		where
			pg_cl.relnamespace = pg_ns.oid
				and
			pg_cl.oid in (
				select inhrelid from pg_inherits where inhparent = (
					select oid from pg_class where
						relnamespace = (select oid from pg_namespace where nspname = ''''audit'''')
							and
						relname = ''''audit_trail''''
				)
			)
	'');
	-- loop over audit log tables
	FOR __audit_table__name, __audit_table__table_oid IN
		EXECUTE __SQL__get_log_tables
	LOOP
		RAISE NOTICE ''processing audit.% (oid %)'', __audit_table__name, __audit_table__table_oid;
		FOREACH __col2drop IN ARRAY __cols2drop LOOP
			__SQL := format(
				''alter table audit.%s drop column if exists %s cascade'',
				__audit_table__name,
				__col2drop
			);
			EXECUTE __SQL;
		END LOOP;
	END LOOP;
	RAISE NOTICE ''done'';
END';

select staging.drop_legacy_log_columns();

drop function if exists staging.drop_legacy_log_columns() cascade;

-- --------------------------------------------------------------
-- .pk_audit
DO 'BEGIN
		alter table audit.audit_trail rename column pk_audit to pk_audit_trail;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.pk_audit does not exist'';
	END
';
comment on column audit.audit_trail.pk_audit_trail is 'the primary key for this log entry,
not related to the primary key of the logged row,
unique within the audit logging system';


-- .orig_tableoid
DO 'BEGIN
		alter table audit.audit_trail rename column orig_tableoid to src_table_oid;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.orig_tableoid does not exist'';
	END
';
comment on column audit.audit_trail.src_table_oid is
	'the OID of the table this log entry comes from (TG_RELID when the audit trigger ran)';


-- .orig_version -> .row_version
DO 'BEGIN
		alter table audit.audit_trail rename column orig_version to row_version;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.orig_version does not exist'';
	END
';

alter table audit.audit_trail
	alter column row_version
		drop default;

comment on column audit.audit_trail.row_version is
'value of .row_version of the row in the table this log entry comes from,
IOW, which row version was turned into this log entry';


--.orig_by
DO 'BEGIN
		alter table audit.audit_trail rename column orig_by to version_created_by;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.orig_by does not exist'';
	END
';
comment on column audit.audit_trail.version_created_by is
'value of .modified_by of the row in the table this log entry comes from,
IOW, who created the row version that this log entry represents,';


-- .orig_when
DO 'BEGIN
		alter table audit.audit_trail rename column orig_when to version_created_when;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.orig_when does not exist'';
	END
';
comment on column audit.audit_trail.version_created_when is
'value of .modified_when of the row in the table this log entry comes from,
IOW, the creation timestamp of the row version this log entry represents,
(not of this log record itself, for that see .version_logged_when)';


-- .audit_action
DO 'BEGIN
		alter table audit.audit_trail rename column audit_action to version_logged_why;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.audit_action does not exist'';
	END
';
comment on column audit.audit_trail.version_logged_why is
	'Why was this log entry created (UPDATE or DELETE to the original row).';


-- .audit_by
DO 'BEGIN
		alter table audit.audit_trail rename column audit_by to version_logged_by;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.audit_by does not exist'';
	END
';
comment on column audit.audit_trail.version_logged_by is
'Who created this log entry.
Should be equal to .modified_by of the *next* version of the logged row.';


-- audit_when
DO 'BEGIN
		alter table audit.audit_trail rename column audit_when to version_logged_when;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.audit_when does not exist'';
	END
';
comment on column audit.audit_trail.version_logged_when is
	'When was this log entry created (not when the logged row was created).';

-- -------------------------------------------------------------------
-- new column in audit trail tables
alter table audit.audit_trail
	add column if not exists src_row_pk_audit integer;

comment on column audit.audit_trail.src_row_pk_audit is
'Value of .pk_audit of row in table this log entry came from,
uniquely identifies this row, regardless of version, and regardless of which child table it is in';

drop function if exists staging.fill_in__audit_trail__pk_audit() cascade;

create function staging.fill_in__audit_trail__pk_audit()
	returns void
	language plpgsql
	as '
DECLARE
	__SQL text;
	__SQL_update_audit_row text;
	__table_exists bool;
	__audit_table__name text;
	__audit_table__table_oid oid;
	__src_table__table_oid oid;
	__src_table__pk_name text;
	__audit_row record;
	__pk_audit_in_src_row integer;
BEGIN
	RAISE NOTICE ''filling in new column .pk_audit in audit trail tables'';
	-- allow updates
	DROP RULE IF EXISTS audit_trail_no_upd ON audit.audit_trail CASCADE;
	-- loop over audit log tables
	FOR __audit_table__name, __audit_table__table_oid IN
		select
			pg_cl.relname,
			pg_cl.oid
		from
			pg_namespace pg_ns,
			pg_class pg_cl
		where
			pg_cl.relnamespace = pg_ns.oid
				and
			pg_cl.oid in (
				select inhrelid from pg_inherits where inhparent = (
					select oid from pg_class where
						relnamespace = (select oid from pg_namespace where nspname = ''audit'') and
						relname = ''audit_trail''
				)
			)
	LOOP
		RAISE NOTICE ''processing audit.% (oid %)'', __audit_table__name, __audit_table__table_oid;
		__SQL := format(''select src_table_oid from audit.%s limit 1'', __audit_table__name);
		EXECUTE __SQL INTO __src_table__table_oid;
		IF __src_table__table_oid IS NOT DISTINCT FROM NULL THEN
			RAISE NOTICE ''-> audit.%: no log records to update'', __audit_table__name;
			CONTINUE;
		END IF;

		-- does source table still exist ?
		__SQL := ''select exists(select 1 from pg_class where oid = $1)'';
		EXECUTE __SQL INTO __table_exists USING __src_table__table_oid;
		IF __table_exists IS FALSE THEN
			RAISE NOTICE ''-> audit.%: source table % (oid %) does not exist (probably older table)'', __audit_table__name, CAST(__src_table__table_oid AS regclass), __src_table__table_oid;
			CONTINUE;
		END IF;

		-- get name of primary key column
		__SQL := format (''
			SELECT pg_attribute.attname AS pk_col
			FROM pg_index, pg_class, pg_attribute, pg_namespace
			WHERE
				pg_class.oid = $1
					AND
				indrelid = pg_class.oid
					AND
				pg_class.relnamespace = pg_namespace.oid
					AND
				pg_attribute.attrelid = pg_class.oid
					AND
				pg_attribute.attnum = any(pg_index.indkey)
					AND
				indisprimary
		'');
		EXECUTE __SQL INTO __src_table__pk_name USING __src_table__table_oid;
		RAISE NOTICE ''-> audit.%: updating from % (oid %) via PK column %'', __audit_table__name, CAST(__src_table__table_oid AS regclass), __src_table__table_oid, __src_table__pk_name;
		__SQL := format (
			''select pk_audit_trail, %s as pk from %s order by pk'',
			__src_table__pk_name,
			CAST(__audit_table__table_oid AS regclass)
		);
		-- loop over rows in this audit log table
		FOR __audit_row IN EXECUTE __SQL LOOP
			EXECUTE format (
				''select pk_audit from %s where %s = $1'',
				CAST(__src_table__table_oid AS regclass),
				__src_table__pk_name
			) INTO __pk_audit_in_src_row
			USING __audit_row.pk;
--			RAISE NOTICE ''%:  pk_audit:%  src.pk:% (pk_audit_trail:%)'', __SQL_update_audit_row, __pk_audit_in_src_row, __audit_row.pk, __audit_row.pk_audit_trail;
			__SQL_update_audit_row := format (
				''update %s SET src_row_pk_audit = coalesce (
						$1,
						nextval(pg_get_serial_sequence(''''audit.audit_fields'''', ''''pk_audit''''))
					)
				  WHERE %s = $2'',
				CAST(__audit_table__table_oid AS regclass),
				__src_table__pk_name
			);
			EXECUTE __SQL_update_audit_row USING __pk_audit_in_src_row, __audit_row.pk;
		END LOOP;
	END LOOP;
	-- fill in pk_audit values in log tables whose logged tables do not exist anymore...
	update audit.audit_trail
		set src_row_pk_audit = nextval(pg_get_serial_sequence(''audit.audit_fields'', ''pk_audit''))
		where src_row_pk_audit IS NULL
	;
	-- increment row_version in log tables as we now start with row_version = 1 on INSERT
	update audit.audit_trail set row_version = row_version + 1;
	-- disallow updates again
	CREATE RULE audit_trail_no_upd AS ON UPDATE TO audit.audit_trail DO INSTEAD NOTHING;
	RAISE NOTICE ''done'';
END;';

select staging.fill_in__audit_trail__pk_audit();

drop function if exists staging.fill_in__audit_trail__pk_audit() cascade;

alter table audit.audit_trail
	alter column src_row_pk_audit
		set not null;

-- -------------------------------------------------------------------
alter table audit.audit_trail
	drop constraint if exists audit__audit_trail__uniq_row_version_per_row;

alter table audit.audit_trail
	add constraint audit__audit_trail__uniq_row_version_per_row
		unique (src_row_pk_audit, row_version);

-- --------------------------------------------------------------
alter table audit.audit_fields
	drop constraint if exists audit__audit_fields__uniq_row_version_per_row;

alter table audit.audit_fields
	add constraint audit__audit_fields__uniq_row_version_per_row
		unique (pk_audit, row_version);

-- --------------------------------------------------------------
drop view if exists audit.v_audit_trail cascade;

create or replace view audit.v_audit_trail as
	-- all audit log tables are children of audit.audit_trail
	select
		to_char(a_at.version_logged_when, 'YYYY-MM-DD HH24:MI')
			as event_when,
		coalesce (
			(select short_alias from dem.staff where db_user = a_at.version_logged_by),
			'<' || a_at.version_logged_by || '>'
		)
			as event_by,
		a_at.src_table_oid::regclass
			as event_table,
		a_at.row_version
			as row_version_before,
		case
			when a_at.version_logged_why = 'DELETE' then NULL::integer
			else (a_at.row_version + 1)
		end
			as row_version_after,
		a_at.version_logged_why
			as event,
		a_at.version_logged_when
			as event_when_ts,
		a_at.src_row_pk_audit
			as pk_audit
	from
		audit.audit_trail a_at

union all

	select
		to_char(g_al.modified_when, 'YYYY-MM-DD HH24:MI')
			as event_when,
		coalesce (
			(select short_alias from dem.staff where db_user = g_al.modified_by),
			'<' || g_al.modified_by || '>'
		)
			as event_by,
		'gm.access_log'::regclass
			as event_table,
		NULL::integer
			as row_version_before,
		1::integer
			as row_version_after,
		g_al.user_action
			as event,
		g_al.modified_when
			as event_when_ts,
		g_al.pk_audit
			as pk_audit
	from
		gm.access_log g_al
	where
		g_al.row_version = 1


union all

	-- all original data tables are children of audit.audit_fields
	select
		to_char(a_af.modified_when, 'YYYY-MM-DD HH24:MI')
			as event_when,
		coalesce (
			(select short_alias from dem.staff where db_user = a_af.modified_by),
			'<' || a_af.modified_by || '>'
		)
			as event_by,
		a_af.tableoid::regclass
			as event_table,
		NULL::integer
			as row_version_before,
		1::integer
			as row_version_after,
		'INSERT'::text
			as event,
		a_af.modified_when
			as event_when_ts,
		a_af.pk_audit
			as pk_audit
	from
		audit.audit_fields a_af
	where
		a_af.row_version = 1
;

grant select on audit.v_audit_trail to group "gm-doctors";

-- --------------------------------------------------------------
-- this dance is necessary
-- -.gm.log_script_insertion relies on a default for .row_version
-- - we have to drop the INSERT trigger overriding .row_version (because
--   audit column names changed so the existing trigger would fail, and
--   it would also deliver the now-wrong default 0)
drop function if exists audit.ft_ins_access_log cascade;
alter table audit.audit_fields alter column row_version set default 1;
select gm.log_script_insertion('v23-audit-audit_trail-dynamic.sql', 'v23');
alter table audit.audit_fields alter column row_version drop default;
