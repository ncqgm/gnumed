-- GnuMed auditing functionality
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmAudit.sql,v $
-- $Revision: 1.15 $
-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create schema audit authorization "gm-dbo";

-- ===================================================================
create table audit.audited_tables (
	id serial primary key,
	schema name
		not null
		default 'public',
	table_name name
		not null,
	unique(schema, table_name)
);

-- ===================================================================
create table audit.audit_fields (
	pk_audit serial
		primary key,
	row_version integer
		not null
		default 0,
	modified_when timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	modified_by name
		not null
		default CURRENT_USER
);

-- ===================================================================
create table audit.audit_trail (
	pk_audit serial
		primary key,
	orig_version integer
		not null
		default 0,
	orig_when timestamp with time zone
		not null,
	orig_by name
		not null,
	orig_tableoid oid	
		not null,
	audit_action text
		not null
		check (audit_action in ('UPDATE', 'DELETE')),
	audit_when timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	audit_by name
		not null
		default CURRENT_USER
);

-- ===================================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmAudit.sql,v $';
insert into gm_schema_revision (filename, version) values ('$RCSfile: gmAudit.sql,v $', '$Revision: 1.15 $');

-- ===================================================================
-- $Log: gmAudit.sql,v $
-- Revision 1.15  2006-01-05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.14  2005/12/04 09:37:25  ncq
-- - same here, hold style of logging script insertion needed
--
-- Revision 1.13  2005/11/25 15:01:05  ncq
-- - better factor out dynamic stuff
--
-- Revision 1.12  2005/10/24 19:08:11  ncq
-- - re-runnables factored out
-- - set default for audited_tables.schema to public
--
-- Revision 1.11  2005/09/19 16:38:51  ncq
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
