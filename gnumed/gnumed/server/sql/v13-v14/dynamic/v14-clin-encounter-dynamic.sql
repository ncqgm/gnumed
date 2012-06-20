-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select audit.add_table_for_audit('clin', 'encounter');

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-encounter-dynamic.sql', 'Revision: 1.1');
