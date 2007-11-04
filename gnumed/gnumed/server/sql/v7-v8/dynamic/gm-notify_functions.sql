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
-- $Id: gm-notify_functions.sql,v 1.4 2007-11-04 23:00:29 ncq Exp $
-- $Revision: 1.4 $

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
	 where the :<identity_pk> is only added if the notify trigger knows how.';

comment on column gm.notifying_tables.carries_identity_pk is
	'Whether or not the signal delivers the PK of the
	 related identity. Set during bootstrapping.';

-- ==============================================================
\unset ON_ERROR_STOP
drop function public.add_table_for_notifies(name, name, name) cascade;
drop function public.add_table_for_notifies(name, name) cascade;
-- the old one:
drop function public.add_table_for_notifies(name) cascade;
\set ON_ERROR_STOP 1

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
select gm.log_script_insertion('$RCSfile: gm-notify_functions.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: gm-notify_functions.sql,v $
-- Revision 1.4  2007-11-04 23:00:29  ncq
-- - add missing ;
--
-- Revision 1.3  2007/10/30 12:53:55  ncq
-- - reintroduce attach_identity_pk as carries_identity_pk
--
-- Revision 1.2  2007/10/30 08:32:15  ncq
-- - no more attach_identity_pk needed
--
-- Revision 1.1  2007/10/23 21:18:12  ncq
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
