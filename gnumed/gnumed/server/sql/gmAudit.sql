-- GnuMed auditing functionality
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmAudit.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table audit_mark (
	pk_audit serial primary key,
	row_version integer not null default 0,
	modify_when timestamp with time zone not null default CURRENT_TIMESTAMP,
	modify_by name not null default CURRENT_USER
);

comment on table audit_mark is
	'All tables that need standard auditing must inherit from this table.
	 Marks tables for automatic audit trigger generation';
comment on column audit_mark.row_version is
	'the version of the row; mainly just a count';
comment on COLUMN audit_mark.modify_when is
	'when has this row been committed (created/modified)';
comment on COLUMN audit_mark.modify_by is
	'by whom has this row been committed (created/modified)';

-- ===================================================================
create table audit_log (
	pk_audit serial primary key,
	orig_version integer not null default 0,
	orig_when timestamp with time zone not null,
	orig_by name not null,
	orig_tableoid oid not null,
	audit_action varchar(6) not null check (audit_action in ('UPDATE', 'DELETE')),
	audit_when timestamp with time zone not null default CURRENT_TIMESTAMP,
	audit_by name not null default CURRENT_USER
);

comment on table audit_log is
	'Each table that needs standard auditing must have a log table inheriting
	 from this table. Log tables have the same name with a prepended "log_".
	 However, log_* tables shall not have constraints.';
comment on column audit_log.orig_version is
	'the version of this row in the original table previous to the modification';
comment on column audit_log.orig_when is
	'previous modification date in the original table';
comment on column audit_log.orig_by is
	'who committed the row to the original table';
comment on column audit_log.orig_tableoid is
	'the table oid of the original table, use this to identify the source table';
comment on column audit_log.audit_action is
	'either "update" or "delete"';
comment on column audit_log.audit_when is
	'when committed to this table for auditing';
comment on column audit_log.audit_by is
	'committed to this table for auditing by whom';

-- ===================================================================
grant SELECT, UPDATE, INSERT, DELETE on
	"audit_mark",
	"audit_mark_pk_audit_seq",
	"audit_log",
	"audit_log_pk_audit_seq"
to group "_gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmAudit.sql,v $', '$Revision: 1.3 $');

-- ===================================================================
-- $Log: gmAudit.sql,v $
-- Revision 1.3  2003-05-13 14:40:54  ncq
-- - remove check constraints, they are done by triggers now
--
-- Revision 1.2  2003/05/12 19:29:45  ncq
-- - first stab at real auditing
--
-- Revision 1.1  2003/05/12 14:14:53  ncq
-- - first shot at generic auditing tables
--
