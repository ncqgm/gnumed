-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbertq@gmx.net
-- 
-- ==============================================================
-- $Id: v10-adjust-gm_dbo.sql,v 1.1 2008-12-01 12:10:52 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter role "gm-dbo" createrole;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-adjust-gm_dbo.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-adjust-gm_dbo.sql,v $
-- Revision 1.1  2008-12-01 12:10:52  ncq
-- - gm-dbo can now create roles
--
--