-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.lab_request
	add column note_test_org text;


alter table audit.log_lab_request
	add column note_test_org text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lab_request-static.sql', '16.0');
