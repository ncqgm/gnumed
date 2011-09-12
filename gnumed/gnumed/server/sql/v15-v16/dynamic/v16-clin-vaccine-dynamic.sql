-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.vaccine
	alter column is_live
		set default true;

-- ==============================================================
select gm.log_script_insertion('v16-clin-vaccine-dynamic.sql', 'v16');
