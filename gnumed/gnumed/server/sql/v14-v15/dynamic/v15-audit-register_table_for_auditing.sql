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

-- --------------------------------------------------------------
create or replace function audit.register_table_for_auditing(name, name)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_schema alias for $1;
	_table alias for $2;
BEGIN
	-- does table exist ?
	perform 1 from pg_class where
		relname = _table
			and
		relnamespace = (select oid from pg_namespace where nspname = _schema)
	;

	if not found then
		raise exception ''audit.register_table_for_auditing(): table [%.%] does not exist'', _schema, _table;
		return false;
	end if;

	-- already queued for auditing ?
	perform 1 from audit.audited_tables where
		table_name = _table
			and
		schema = _schema;

	if found then
		return true;
	end if;

	-- add definition
	insert into audit.audited_tables (
		schema, table_name
	) values (
		_schema, _table
	);

	return true;
END;';

comment on function audit.register_table_for_auditing(name, name) is
	'sanity-checking convenience function for registering a table for auditing';

-- --------------------------------------------------------------
-- legacy functions
\unset ON_ERROR_STOP
drop function audit.add_table_for_audit(name, name) cascade;
drop function audit.add_table_for_audit(name) cascade;
\set ON_ERROR_STOP 1

create function audit.add_table_for_audit(name, name)
	returns boolean
	language SQL
	as 'select audit.register_table_for_auditing($1, $2);'
;

create function audit.add_table_for_audit(name)
	returns boolean
	language SQL
	as E'select audit.register_table_for_auditing(''public'', $1);'
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-audit-register_table_for_auditing.sql', 'Revision: 1.0');
