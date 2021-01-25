-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-clin-v_emr_journal-fixup.sql,v 1.2 2009-05-18 09:46:55 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- remember to handle dependent objects possibly dropped by CASCADE
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
select gm.log_script_insertion('$RCSfile: v10-clin-v_emr_journal-fixup.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-clin-v_emr_journal-fixup.sql,v $
-- Revision 1.2  2009-05-18 09:46:55  ncq
-- - new
--
-- Revision 1.1.2.2  2009/03/28 14:04:46  ncq
-- - comment out default parm tweaking
--
-- Revision 1.1.2.1  2009/03/28 13:54:29  ncq
-- - fix use of coalesce()
--
--