-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .status
alter table clin.test_result add column status text;

alter table audit.log_test_result add column status text;

-- --------------------------------------------------------------
-- .source_data
alter table clin.test_result add column source_data text;

alter table audit.log_test_result add column source_data text;

-- --------------------------------------------------------------
-- .val_grouping
alter table clin.test_result add column val_grouping text;

alter table audit.log_test_result add column val_grouping text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-test_result-static.sql', '20.0');
