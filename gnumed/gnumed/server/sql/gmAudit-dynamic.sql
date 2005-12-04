-- GNUmed auditing functionality
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmAudit-dynamic.sql,v $
-- $Revision: 1.5 $
-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
comment on table audited_tables is
	'All tables that need standard auditing must be
	 recorded in this table. Audit triggers will be
	 generated automatically for all tables recorded
	 here.';

comment on table audit_fields is
	'this table holds all the fields needed for auditing';
comment on column audit_fields.row_version is
	'the version of the row; mainly just a count';
comment on COLUMN audit_fields.modified_when is
	'when has this row been committed (created/modified)';
comment on COLUMN audit_fields.modified_by is
	'by whom has this row been committed (created/modified)';

comment on table audit_trail is
	'Each table that needs standard auditing must have a log table inheriting
	 from this table. Log tables have the same name with a prepended "log_".
	 However, log_* tables shall not have constraints.';
comment on column audit_trail.orig_version is
	'the version of this row in the original table previous to the modification';
comment on column audit_trail.orig_when is
	'previous modification date in the original table';
comment on column audit_trail.orig_by is
	'who committed the row to the original table';
comment on column audit_trail.orig_tableoid is
	'the table oid of the original table, use this to identify the source table';
comment on column audit_trail.audit_action is
	'either "update" or "delete"';
comment on column audit_trail.audit_when is
	'when committed to this table for auditing';
comment on column audit_trail.audit_by is
	'committed to this table for auditing by whom';

-- ===================================================================
create or replace function add_table_for_audit(name, name) returns unknown as '
DECLARE
	_relnamespace alias for $1;
	_relname ALIAS FOR $2;
	dummy RECORD;
	tmp text;
BEGIN
	-- does table exist ?
	select relname into dummy from pg_class where
		relname = _relname and
		relnamespace = (select oid from pg_namespace where nspname = _relnamespace)
	;
	if not found then
		tmp := _relnamespace || \'.\' || _relname;
		raise exception ''add_table_for_audit: Table [%] does not exist.'', tmp;
		return false;
	end if;
	-- already queued for auditing ?
	select 1 into dummy from audited_tables where table_name = _relname and schema = _relnamespace;
	if found then
		return true;
	end if;
	-- add definition
	insert into audited_tables (
		schema, table_name
	) values (
		_relnamespace, _relname
	);
	return true;
END;' language 'plpgsql';

comment on function add_table_for_audit (name, name) is
	'sanity-checking convenience function for marking tables for auditing';


create or replace function add_table_for_audit(name) returns unknown as '
	select add_table_for_audit(\'public\', $1);
' language SQL;

comment on function add_table_for_audit(name) is
	'sanity-checking convenience function for marking tables
	 for auditing, schema is always "public"';

-- ---------------------------------------------
-- protect from direct inserts/updates/deletes which the
-- inheritance system can't handle properly
\unset ON_ERROR_STOP
drop rule audit_fields_no_ins on audit_fields cascade;
drop rule audit_fields_no_upd on audit_fields cascade;
drop rule audit_fields_no_del on audit_fields cascade;
\set ON_ERROR_STOP 1

-- FIXME: those should actually use PL/pgSQL and raise
--        an exception...
create rule audit_fields_no_ins as
	on insert to audit_fields
	do instead nothing;

create rule audit_fields_no_upd as
	on update to audit_fields
	do instead nothing;

create rule audit_fields_no_del as
	on delete to audit_fields
	do instead nothing;

-- ---------------------------------------------
-- protect from direct inserts/updates/deletes which the
-- inheritance system can't handle properly
\unset ON_ERROR_STOP
drop rule audit_trail_no_ins on audit_trail cascade;
drop rule audit_trail_no_upd on audit_trail cascade;
drop rule audit_trail_no_del on audit_trail cascade;
\set ON_ERROR_STOP 1

-- FIXME: those should actually use PL/pgSQL and raise
--        an exception...
create rule audit_trail_no_ins as
	on insert to audit_trail
	do instead nothing;

create rule audit_trail_no_upd as
	on update to audit_trail
	do instead nothing;

create rule audit_trail_no_del as
	on delete to audit_trail
	do instead nothing;

-- ===================================================================
-- FIXME: actually this should be done by giving "creator"
-- rights to the audit trigger functions
grant SELECT, UPDATE, INSERT, DELETE on
	"audit_fields",
	"audit_fields_pk_audit_seq",
	"audit_trail",
	"audit_trail_pk_audit_seq"
to group "gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
-- keep the "true" !
delete from gm_schema_revision where filename = '$RCSfile: gmAudit-dynamic.sql,v $';
insert into gm_schema_revision (filename, version) values ('$RCSfile: gmAudit-dynamic.sql,v $', '$Revision: 1.5 $');

-- ===================================================================
-- $Log: gmAudit-dynamic.sql,v $
-- Revision 1.5  2005-12-04 09:36:52  ncq
-- - need to use explicit and old style of logging script insertion
--   due to early running in upgrade process
--
-- Revision 1.4  2005/11/29 19:04:51  ncq
-- - must use *old* log_script_insertion
--
-- Revision 1.3  2005/11/25 15:01:05  ncq
-- - better factor out dynamic stuff
--
-- Revision 1.2  2005/10/24 19:06:51  ncq
-- - missing ";"
-- - wrong column for pg_namespace
--
-- Revision 1.1  2005/10/24 17:56:33  ncq
-- - factor out re-runnables for auditing
--
