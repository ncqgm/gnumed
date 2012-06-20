-- GNUmed auditing functionality
-- ===================================================================
-- license: GPL v2 or later
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
