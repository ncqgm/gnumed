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
create or replace function gm.xid2int(xid)
	returns integer
	language 'sql'
	as 'select $1::text::integer;';

-- ==============================================================
create or replace function gm.register_notifying_table(name, name, name)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_namespace alias for $1;
	_table alias for $2;
	_signal alias for $3;
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
		and schema_name = _namespace
		and signal = _signal;

	insert into gm.notifying_tables (
		schema_name,
		table_name,
		signal
	) values (
		_namespace,
		_table,
		_signal
	);

	return true;
END;';

comment on function gm.register_notifying_table(name, name, name) is
	'Register given table for notification trigger generator. Parameters are: (schema, table, signal name)';

-- --------------------------------------------------------------
create or replace function gm.register_notifying_table(name, name)
	returns boolean
	language SQL
	as 'select gm.register_notifying_table($1, $2, $2);'
;

comment on function gm.register_notifying_table(name, name) is
	'Mark given table for notification trigger generator. Parameters are: (schema, table). Defaults signal to table name.';

-- --------------------------------------------------------------
-- legacy functions:

create or replace function gm.add_table_for_notifies(name, name, name)
	returns boolean
	language SQL
	as 'select gm.register_notifying_table($1, $2, $3);'
;

create or replace function gm.add_table_for_notifies(name, name)
	returns boolean
	language SQL
	as 'select gm.add_table_for_notifies($1, $2, $2);'
;

-- --------------------------------------------------------------
grant insert on
	gm.access_log
to group "gm-public";

grant usage on
	gm.access_log_pk_seq
to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-gm-register_notifying_table.sql', 'Revision: 1.0');

-- ==============================================================
