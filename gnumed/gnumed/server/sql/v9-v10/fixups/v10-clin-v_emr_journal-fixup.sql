-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten.Hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-clin-v_emr_journal-fixup.sql,v 1.1.2.1 2009-03-28 13:54:29 ncq Exp $
-- $Revision: 1.1.2.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop view clin.v_emr_journal cascade;
\set ON_ERROR_STOP 1


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
select gm.log_script_insertion('$RCSfile: v10-clin-v_emr_journal-fixup.sql,v $', '$Revision: 1.1.2.1 $');

-- ==============================================================
-- $Log: v10-clin-v_emr_journal-fixup.sql,v $
-- Revision 1.1.2.1  2009-03-28 13:54:29  ncq
-- - fix use of coalesce()
--
--