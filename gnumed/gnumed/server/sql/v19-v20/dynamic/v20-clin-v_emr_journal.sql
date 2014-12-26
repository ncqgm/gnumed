-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_emr_journal cascade;


create view clin.v_emr_journal as

	select * from clin.v_pat_narrative_journal

union all

	select * from clin.v_health_issues_journal

union all

	select * from clin.v_pat_encounters_journal

union all

	select * from clin.v_pat_episodes_journal

union all

	select * from clin.v_family_history_journal

union all

	select *, 0 as row_version from clin.v_pat_allergies_journal

union all

	select * from clin.v_pat_allergy_state_journal

union all

	select * from clin.v_test_results_journal

union all

	select * from clin.v_hospital_stays_journal

union all

	select *, 0 as row_version from blobs.v_doc_med_journal

union all

	select * from clin.v_pat_substance_intake_journal

union all

	select * from clin.v_procedures_journal

union all

	select * from clin.v_pat_vaccinations_journal

union all

	select * from clin.v_suppressed_hints_journal

union all

	select * from clin.v_external_care_journal
;

comment on view clin.v_emr_journal is
	'Clinical patient data formatted into one string per
	 clinical entity even if it constains several user-
	 visible fields. Mainly useful for display as a simple
	 EMR journal.';


grant select on clin.v_emr_journal to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-v_emr_journal.sql', '20.0');
