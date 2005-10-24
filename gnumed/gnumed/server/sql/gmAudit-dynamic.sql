-- GNUmed auditing functionality
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmAudit-dynamic.sql,v $
-- $Revision: 1.2 $
-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

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


-- drop function add_table_for_audit(name) cascade;
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmAudit-dynamic.sql,v $', '$Revision: 1.2 $');

-- ===================================================================
-- $Log: gmAudit-dynamic.sql,v $
-- Revision 1.2  2005-10-24 19:06:51  ncq
-- - missing ";"
-- - wrong column for pg_namespace
--
-- Revision 1.1  2005/10/24 17:56:33  ncq
-- - factor out re-runnables for auditing
--
