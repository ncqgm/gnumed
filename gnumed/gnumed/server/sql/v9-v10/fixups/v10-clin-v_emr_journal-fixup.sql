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
-- remember to handle dependent objects possibly dropped by CASCADE
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

	select * from clin.v_hx_family_journal

union all

	select * from clin.v_pat_allergies_journal

union all

	select * from clin.v_pat_allergy_state_journal

union all

	select * from clin.v_test_results_journal

union all

	select * from blobs.v_doc_med_journal

;


comment on view clin.v_emr_journal is
	'Clinical patient data formatted into one string per
	 clinical entity even if it constains several user-
	 visible fields. Mainly useful for display as a simple
	 EMR journal.';


grant select on clin.v_emr_journal to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_emr_journal-fixup.sql,v $', '$Revision: 1.2 $');
