-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------

delete from audit.audited_tables
where
	schema = 'clin'
		and
	table_name = 'operation'
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-operation-dynamic.sql', 'v16');

-- ==============================================================
