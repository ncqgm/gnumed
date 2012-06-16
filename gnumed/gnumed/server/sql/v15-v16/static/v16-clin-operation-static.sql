-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop table clin.operation cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-operation-static.sql', '16.0');
