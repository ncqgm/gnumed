-- GnuMed auditing functionality
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmAudit.sql,v $
-- $Revision: 1.11 $
-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table audited_tables (
	id serial primary key,
	schema name default null,
	table_name name unique not null
);

comment on table audited_tables is
	'All tables that need standard auditing must be
	 recorded in this table. Audit triggers will be
	 generated automatically for all tables recorded
	 here.';

-- ===================================================================
\unset ON_ERROR_STOP
drop function add_table_for_audit (name);
\set ON_ERROR_STOP 1

create function add_table_for_audit (name) returns unknown as '
DECLARE
	tbl_name ALIAS FOR $1;
	dummy RECORD;
BEGIN
	-- does table exist ?
	select relname into dummy from pg_class where relname = tbl_name;
	if not found then
		raise exception ''add_table_for_audit: Table [%] does not exist.'', tbl_name;
		return false;
	end if;
	-- add definition
	insert into audited_tables (
		table_name
	) values (
		tbl_name
	);
	return true;
END;' language 'plpgsql';

comment on function add_table_for_audit (name) is
	'sanity-checking convenience function for marking tables for auditing';

-- ===================================================================
create table audit_fields (
	pk_audit serial primary key,
	row_version integer not null default 0,
	modified_when timestamp with time zone not null default CURRENT_TIMESTAMP,
	modified_by name not null default CURRENT_USER
);

comment on table audit_fields is
	'this table holds all the fields needed for auditing';
comment on column audit_fields.row_version is
	'the version of the row; mainly just a count';
comment on COLUMN audit_fields.modified_when is
	'when has this row been committed (created/modified)';
comment on COLUMN audit_fields.modified_by is
	'by whom has this row been committed (created/modified)';

-- ---------------------------------------------
-- protect from direct inserts/updates/deletes which the
-- inheritance system can't handle properly
\unset ON_ERROR_STOP
drop rule audit_fields_no_ins on audit_fields cascade;
drop rule audit_fields_no_ins;
drop rule audit_fields_no_upd on audit_fields cascade;
drop rule audit_fields_no_upd;
drop rule audit_fields_no_del on audit_fields cascade;
drop rule audit_fields_no_del;
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

-- ===================================================================
create table audit_trail (
	pk_audit serial primary key,
	orig_version integer not null default 0,
	orig_when timestamp with time zone not null,
	orig_by name not null,
	orig_tableoid oid not null,
	audit_action text not null check (audit_action in ('UPDATE', 'DELETE')),
	audit_when timestamp with time zone not null default CURRENT_TIMESTAMP,
	audit_by name not null default CURRENT_USER
);

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

-- ---------------------------------------------
-- protect from direct inserts/updates/deletes which the
-- inheritance system can't handle properly
\unset ON_ERROR_STOP
drop rule audit_trail_no_ins on audit_trail cascade;
drop rule audit_trail_no_ins;
drop rule audit_trail_no_upd on audit_trail cascade;
drop rule audit_trail_no_upd;
drop rule audit_trail_no_del on audit_trail cascade;
drop rule audit_trail_no_del;
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmAudit.sql,v $', '$Revision: 1.11 $');

-- ===================================================================
-- $Log: gmAudit.sql,v $
-- Revision 1.11  2005-09-19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.10  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.9  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.8  2004/09/22 14:10:38  ncq
-- - add RULEs to protect audit_trail/audit_fields parent
--   tables from direct insert/update/delete to preserve
--   referential integrity
--
-- Revision 1.7  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.6  2003/10/01 15:45:20  ncq
-- - use add_table_for_audit() instead of inheriting from audit_mark
--
-- Revision 1.5  2003/06/29 15:22:50  ncq
-- - split audit_fields off of audit_mark, they really
--   are two separate if related things
--
-- Revision 1.4  2003/05/22 12:55:19  ncq
-- - table audit_log -> audit_trail
--
-- Revision 1.3  2003/05/13 14:40:54  ncq
-- - remove check constraints, they are done by triggers now
--
-- Revision 1.2  2003/05/12 19:29:45  ncq
-- - first stab at real auditing
--
-- Revision 1.1  2003/05/12 14:14:53  ncq
-- - first shot at generic auditing tables
--
