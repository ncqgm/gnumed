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
-- $Id: add_notification_signals.sql,v 1.1 2007-10-30 08:28:21 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.add_table_for_notifies('blobs'::name, 'doc_med'::name, 'doc'::name);
select gm.add_table_for_notifies('blobs'::name, 'doc_obj'::name, 'doc_page'::name);

select gm.add_table_for_notifies('dem'::name, 'provider_inbox'::name);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: add_notification_signals.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: add_notification_signals.sql,v $
-- Revision 1.1  2007-10-30 08:28:21  ncq
-- - add signals to tables
--
--
