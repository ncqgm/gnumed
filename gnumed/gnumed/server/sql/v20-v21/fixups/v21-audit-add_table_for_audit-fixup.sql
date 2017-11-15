-- GNUmed auditing functionality
-- ===================================================================
-- license: GPL v2 or later
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop function if exists audit.add_table_for_audit(name, name) cascade;

create or replace function audit.add_table_for_audit(name, name)
	returns boolean
	language 'plpgsql'
	security definer
	as '
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
		tmp := _relnamespace || ''.'' || _relname;
		raise exception ''audit.add_table_for_audit: Table [%] does not exist.'', tmp;
		return false;
	end if;
	-- already queued for auditing ?
	select 1 into dummy from audit.audited_tables where table_name = _relname and schema = _relnamespace;
	if found then
		return true;
	end if;
	-- add definition
	insert into audit.audited_tables (
		schema, table_name
	) values (
		_relnamespace, _relname
	);
	return true;
END;';

comment on function audit.add_table_for_audit (name, name) is
	'sanity-checking convenience function for marking tables for auditing';


drop function if exists audit.add_table_for_audit(name) cascade;

create or replace function audit.add_table_for_audit(name)
	returns boolean
	language SQL
	security definer
	as '
select audit.add_table_for_audit(''public'', $1);';

comment on function audit.add_table_for_audit(name) is
	'sanity-checking convenience function for marking tables
	 for auditing, schema is always "public"';

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-audit-add_table_for_audit-fixup.sql', '21.16');
