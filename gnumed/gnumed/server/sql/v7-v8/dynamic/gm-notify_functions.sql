-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v7
-- Target database version: v8
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: gm-notify_functions.sql,v 1.1 2007-10-23 21:18:12 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table gm.notifying_tables is
	'All tables that want to send standard notifications
	 must be recorded in this table. Notification triggers
	 will be generated automatically for all tables recorded
	 here.';

comment on column gm.notifying_tables.signal is
	'The name of the signal to send via NOTIFY.
	 The actual name of the signal will be "<signal>_mod_db:<identity_pk>"
	 where the :<identity_pk> is only added if attach_identity_py is True.';
comment on column gm.notifying_tables.attach_identity_pk is
	'Whether or not to attach to the signal the PK of the identity
	 the inserted/updated/deleted rows pertain to if applicable.
	 The PK will be separated from the signal name by a ":" if so.';

-- ==============================================================
\unset ON_ERROR_STOP
drop function public.add_table_for_notifies(name, name, name) cascade;
drop function public.add_table_for_notifies(name, name) cascade;
drop function public.add_table_for_notifies(name) cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create or replace function gm.add_table_for_notifies(name, name, name, boolean)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_namespace alias for $1;
	_table alias for $2;
	_signal alias for $3;
	_attach_pk alias for $4;
	dummy RECORD;
	tmp text;
BEGIN
	-- does table exist ?
	select relname into dummy from pg_class where
		relname = _table and
		relnamespace = (select oid from pg_namespace where nspname = _namespace)
	;
	if not found then
		tmp := _namespace || \'.\' || _table;
		raise exception ''add_table_for_notifies: Table [%] does not exist.'', tmp;
	end if;

	-- make sure we can insert
	delete from gm.notifying_tables where table_name = _table and schema_name = _namespace;
	insert into gm.notifying_tables (
		schema_name,
		table_name,
		signal,
		attach_identity_pk
	) values (
		_namespace,
		_table,
		_signal,
		_attach_pk
	);

	return true;
END;';

comment on function gm.add_table_for_notifies (name, name, name, boolean) is
	'Mark given table for notification trigger generator.
	 Parameters are: (schema, table, signal name, attach identity pk)';

-- --------------------------------------------------------------
create or replace function gm.add_table_for_notifies(name, name, name)
	returns boolean
	language SQL
	as 'select gm.add_table_for_notifies($1, $2, $3, True);'
;

comment on function gm.add_table_for_notifies (name, name, name) is
	'Mark given table for notification trigger generator.
	 Parameters are: (schema, table, signal).
	 Defaults attach_pk to true.';

-- --------------------------------------------------------------
create or replace function gm.add_table_for_notifies(name, name, boolean)
	returns boolean
	language SQL
	as 'select gm.add_table_for_notifies($1, $2, $2, $3);'
;

comment on function gm.add_table_for_notifies (name, name, boolean) is
	'Mark given table for notification trigger generator.
	 Parameters are: (schema, table, attach_pk).
	 Defaults signal to table name';

-- --------------------------------------------------------------
create or replace function gm.add_table_for_notifies(name, name)
	returns boolean
	language SQL
	as 'select gm.add_table_for_notifies($1, $2, $2, True);'
;

comment on function gm.add_table_for_notifies(name, name) is
	'Mark given table for notification trigger generator.
	 Parameter is (schema, table).
	 Default signal to table name and attach_pk to true.';

-- --------------------------------------------------------------
grant select on gm.notifying_tables to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: gm-notify_functions.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: gm-notify_functions.sql,v $
-- Revision 1.1  2007-10-23 21:18:12  ncq
-- - updated
--
-- Revision 1.7  2007/05/07 16:32:09  ncq
-- - log_script_insertion() now in gm.
--
-- Revision 1.6  2007/01/27 21:16:08  ncq
-- - the begin/commit does not fit into our change script model
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
