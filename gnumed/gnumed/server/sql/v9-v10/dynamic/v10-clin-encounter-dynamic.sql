-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-clin-encounter-dynamic.sql,v 1.1 2008-11-11 21:09:34 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
select gm.add_table_for_notifies('clin', 'encounter');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-encounter-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-encounter-dynamic.sql,v $
-- Revision 1.1  2008-11-11 21:09:34  ncq
-- - add signal
--
--