-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-gm-notifying_tables-dynamic.sql,v 1.1 2009-01-17 22:57:40 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- ==============================================================
alter table gm.notifying_tables
	drop constraint notifying_tables_schema_name_key cascade;

alter table gm.notifying_tables
	add constraint unique_entry
		unique(schema_name, table_name, signal);


-- --------------------------------------------------------------
create or replace function gm.add_table_for_notifies(name, name, name)
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
		raise exception ''add_table_for_notifies: Table [%.%] does not exist.'', _namespace, _table;
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

comment on function gm.add_table_for_notifies (name, name, name) is
	'Mark given table for notification trigger generator.
	 Parameters are: (schema, table, signal name)';

-- --------------------------------------------------------------
create or replace function gm.add_table_for_notifies(name, name)
	returns boolean
	language SQL
	as 'select gm.add_table_for_notifies($1, $2, $2);'
;

comment on function gm.add_table_for_notifies (name, name) is
	'Mark given table for notification trigger generator.
	 Parameters are: (schema, table).
	 Defaults signal to table name.';

-- --------------------------------------------------------------
grant select on gm.notifying_tables to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-gm-notifying_tables-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-gm-notifying_tables-dynamic.sql,v $
-- Revision 1.1  2009-01-17 22:57:40  ncq
-- - new
--
--