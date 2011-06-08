-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-ref-data_source-static.sql,v 1.1 2009-06-10 20:54:41 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table ref.data_source
	add column lang text;

alter table audit.log_data_source
	add column lang text;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-data_source-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-ref-data_source-static.sql,v $
-- Revision 1.1  2009-06-10 20:54:41  ncq
-- - add .lang
--
--