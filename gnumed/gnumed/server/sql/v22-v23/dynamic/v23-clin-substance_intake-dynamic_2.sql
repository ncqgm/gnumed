-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column if exists comment_on_start cascade;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column if exists discontinued cascade;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column if exists discontinue_reason cascade;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column if exists schedule cascade;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column if exists duration cascade;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column if exists is_long_term cascade;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column if exists intake_is_approved_of cascade;

-- --------------------------------------------------------------
--view clin.v_substance_intake_journal depends on column comment_on_start of table clin.substance_intake
--view clin.v_emr_journal depends on view clin.v_substance_intake_journal
--view clin._view_emr_journal_without_suppressed_hints depends on view clin.v_emr_journal

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-substance_intake-dynamic_2.sql', '23.0');
