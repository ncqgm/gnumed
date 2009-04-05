-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten.Hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v11-clin-v_emr_journal.sql,v 1.2 2009-04-05 18:08:01 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop view clin.v_emr_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_emr_journal as

	select *, 0 as row_version from clin.v_pat_narrative_journal

union all

	select * from clin.v_health_issues_journal

union all

	select *, 0 as row_version from clin.v_pat_encounters_journal

union all

	select *, 0 as row_version from clin.v_pat_episodes_journal

union all

	select *, 0 as row_version from clin.v_hx_family_journal

union all

	select *, 0 as row_version from clin.v_pat_allergies_journal

union all

	select * from clin.v_pat_allergy_state_journal

union all

	select *, 0 as row_version from clin.v_test_results_journal

union all

	select * from clin.v_pat_hospital_stays_journal

union all

	select *, 0 as row_version from blobs.v_doc_med_journal

;

comment on view clin.v_emr_journal is
	'Clinical patient data formatted into one string per
	 clinical entity even if it constains several user-
	 visible fields. Mainly useful for display as a simple
	 EMR journal.';


grant select on clin.v_emr_journal to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-v_emr_journal.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-clin-v_emr_journal.sql,v $
-- Revision 1.2  2009-04-05 18:08:01  ncq
-- - health issue view now truly supports row_version
--
-- Revision 1.1  2009/04/01 15:55:40  ncq
-- - new
--
--