-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- ==============================================================
create or replace function gm.register_notifying_table(name, name)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_namespace alias for $1;
	_table alias for $2;
	dummy RECORD;
BEGIN
	-- does table exist ?
	select relname into dummy from pg_class where
		relname = _table and
		relnamespace = (select oid from pg_namespace where nspname = _namespace)
	;
	if not found then
		raise exception ''register_notifying_table(): Table [%.%] does not exist.'', _namespace, _table;
	end if;

	-- make sure we can insert
	delete from gm.notifying_tables where
		table_name = _table
		and schema_name = _namespace;

	insert into gm.notifying_tables (
		schema_name,
		table_name
	) values (
		_namespace,
		_table
	);

	return true;
END;';

comment on function gm.register_notifying_table(name, name) is
	'Register given table for notification trigger generator. Parameters are: (schema, table)';


drop function if exists gm.register_notifying_table(name, name, name) cascade;

-- --------------------------------------------------------------
-- legacy functions:

create or replace function gm.add_table_for_notifies(name, name)
	returns boolean
	language SQL
	as 'select gm.register_notifying_table($1, $2);'
;

drop function if exists gm.add_table_for_notifies(name, name, name) cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-gm-register_notifying_table.sql', '20.0');
