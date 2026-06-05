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
set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop function if exists staging.increment_row_versions_in_logged_tables(_schema_name name, _table_name name) cascade;

create function staging.increment_row_versions_in_logged_tables(_schema_name name, _table_name name)
	returns void
	language plpgsql
	as '
DECLARE
	__SQL text;
	__SQL__get_audited_tables text;
	__logged_table__name text;
	__logged_table__table_oid oid;
	__upd_trigger_func_name text;
	__tables2skip text[];
	__table_count integer;
	__processed_tables text;
BEGIN
	RAISE NOTICE ''incrementing .row_version in child tables of %.%'', _schema_name, _table_name;
	__tables2skip := ARRAY[''clin.clin_root_item'',''clin.review_root'',''clin.lnk_code2item_root''];
	__SQL__get_audited_tables := format (
		''SELECT
			pg_c.relname,
			pg_c.oid
		FROM
			pg_catalog.pg_class pg_c,
			pg_catalog.pg_inherits pg_i
		WHERE
			pg_c.oid = pg_i.inhrelid
				AND
			pg_i.inhparent = ANY(
				SELECT oid FROM pg_class WHERE
					relname = ''''%s''''
						and
					relnamespace = (select oid from pg_namespace where nspname = ''''%s'''')
			)'',
			_table_name,
			_schema_name
	);
	__table_count := 0;
	__processed_tables := '''';
	-- allow updates
	DROP RULE IF EXISTS audit_fields_no_upd ON audit.audit_fields CASCADE;
	FOR __logged_table__name, __logged_table__table_oid IN
		EXECUTE __SQL__get_audited_tables
	LOOP
		__table_count := __table_count + 1;
		__processed_tables := __processed_tables || '' // '' || CAST(__logged_table__table_oid as regclass);
		-- skip intermediate parents and tables lacking triggers
		IF CAST(__logged_table__table_oid as regclass)::text = ANY(__tables2skip) THEN
			RAISE NOTICE ''processing % (oid % = %) -> skipping, intermediate parent'', __logged_table__name, __logged_table__table_oid, CAST(__logged_table__table_oid as regclass);
			CONTINUE;
		END IF;
		__upd_trigger_func_name := format(''audit.ft_upd_%s'', __logged_table__name);
		RAISE NOTICE ''processing % (oid % = %) -> trigger function <%>'', __logged_table__name, __logged_table__table_oid, CAST(__logged_table__table_oid as regclass), __upd_trigger_func_name;
		__SQL := format(''drop function if exists %s cascade'', __upd_trigger_func_name, CAST(__logged_table__table_oid as regclass));
		EXECUTE __SQL;
		-- run update
		__SQL := format(''update %s set row_version = row_version + 1'', CAST(__logged_table__table_oid as regclass));
		EXECUTE __SQL;
	END LOOP;
	-- disallow updates again
	CREATE RULE audit_fields_no_upd AS ON UPDATE TO audit.audit_fields DO INSTEAD NOTHING;
	RAISE NOTICE ''done, table count: %, tables: %'', __table_count, __processed_tables;
END;';

select staging.increment_row_versions_in_logged_tables('audit', 'audit_fields');
select staging.increment_row_versions_in_logged_tables('clin', 'review_root');
select staging.increment_row_versions_in_logged_tables('clin', 'clin_root_item');
select staging.increment_row_versions_in_logged_tables('clin', 'lnk_code2item_root');

drop function if exists staging.increment_row_versions_in_logged_tables(_schema_name name, _table_name name) cascade;

alter table audit.audit_fields
	alter column row_version
		set default 1;

alter table audit.audit_fields
	drop constraint if exists audit__audit_fields__sane_row_version;

alter table audit.audit_fields
	add constraint audit__audit_fields__sane_row_version
		check (row_version > 0);

-- --------------------------------------------------------------
drop function if exists audit.ft_ins_access_log cascade;
select gm.log_script_insertion('v23-audit-audit_fields-increment_row_version.sql', 'v23');
