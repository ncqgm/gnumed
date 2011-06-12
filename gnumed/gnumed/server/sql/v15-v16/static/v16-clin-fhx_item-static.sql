-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-fhx_item-static.sql', 'v16.0');
