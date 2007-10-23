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
-- $Id: gm-notifying_tables.sql,v 1.1 2007-10-23 21:19:36 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table gm.notifying_tables (
	pk serial
		primary key,
	schema_name name
		not null
		default 'public',
	table_name name
		not null,
	signal name
		default null,
	attach_identity_pk boolean
		not null
		default True,
	unique(schema_name, table_name)
);

insert into gm.notifying_tables (schema_name, table_name, signal)
	select schema, table_name, notification_name from public.notifying_tables;

drop table public.notifying_tables cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: gm-notifying_tables.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: gm-notifying_tables.sql,v $
-- Revision 1.1  2007-10-23 21:19:36  ncq
-- - improved
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
