-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_type
	rename column conversion_unit
		to reference_unit;

alter table audit.log_test_type
	rename column conversion_unit
		to reference_unit;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-test_type-static.sql', '20.0');
