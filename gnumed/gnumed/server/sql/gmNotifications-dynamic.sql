-- GNUmed table change notification functionality
-- ===================================================================
-- license: GPL v2 or later
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
comment on table public.notifying_tables is
	'All tables that want to send standard notifications
	 must be recorded in this table. Notification triggers
	 will be generated automatically for all tables recorded
	 here.';

-- ===================================================================
create or replace function add_table_for_notifies(name, name, name)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_relnamespace alias for $1;
	_relname alias for $2;
	_notification_name alias for $3;
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
		raise exception ''add_table_for_notifies: Table [%] does not exist.'', tmp;
		return false;
	end if;
	-- already queued for notification trigger generation ?
	select 1 into dummy from notifying_tables where table_name = _relname and schema = _relnamespace;
	if found then
		return true;
	end if;
	-- add definition
	insert into notifying_tables (
		schema,
		table_name,
		notification_name
	) values (
		_relnamespace,
		_relname,
		_notification_name
	);
	return true;
END;';

comment on function add_table_for_notifies (name, name, name) is
	'Mark given table for notification trigger generator.
	 Parameters are: (schema, table, signal name)';

-- ===================================================================
create or replace function add_table_for_notifies(name, name)
	returns boolean
	language SQL
	as 'select add_table_for_notifies($1, $2, $2);'
;

comment on function add_table_for_notifies (name, name) is
	'Mark given table for notification trigger generator.
	 Parameters are: (schema, table).
	 Uses default notify name.';

-- ===================================================================
create or replace function add_table_for_notifies(name)
	returns boolean
	language SQL
	as 'select add_table_for_notifies(''public''::name, $1, $1);'
;

comment on function add_table_for_notifies(name) is
	'Mark given table for notification trigger generator.
	 Parameter is (table).
	 Assume schema public and use default notify name.';

-- ===================================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmNotifications-dynamic.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmNotifications-dynamic.sql,v $', '$Revision: 1.2 $');

-- ===================================================================
