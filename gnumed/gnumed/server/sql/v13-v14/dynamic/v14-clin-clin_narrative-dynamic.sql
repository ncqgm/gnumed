-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.add_table_for_notifies('clin', 'clin_narrative');

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-clin_narrative-dynamic.sql', 'Revision: 1.1');

