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

	select * from clin.v_pat_allergies_journal

union all

	select * from clin.v_pat_allergy_state_journal

union all

	select * from clin.v_test_results_journal

union all

	select * from clin.v_hospital_stays_journal

union all

	select * from blobs.v_doc_med_journal

union all

	select * from clin.v_intakes_w_o_regimen_journal

union all

	select * from clin.v_intake_regimen_journal

union all

	select * from clin.v_procedures_journal

union all

	select * from clin.v_vaccinations_journal

union all

	select * from clin.v_suppressed_hints_journal

union all

	select * from clin.v_external_care_journal

union all

	select * from clin.v_edc_journal

union all

	select * from clin.v_reminders_journal

;

comment on view clin.v_emr_journal is
	'Clinical patient data formatted into one string per
	 clinical entity even if it constains several user-
	 visible fields. Mainly useful for display as a simple
	 EMR journal.';


grant select on clin.v_emr_journal to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin._view_emr_journal_without_suppressed_hints cascade;

create view clin._view_emr_journal_without_suppressed_hints as
select * from clin.v_emr_journal
where
	src_table != 'clin.suppressed_hint'
;

grant select on clin._view_emr_journal_without_suppressed_hints to group "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_emr_journal.sql', '23.0');
