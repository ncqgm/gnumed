-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten.Hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-clin-v_emr_journal.sql,v 1.2 2008-10-12 15:00:20 ncq Exp $
-- $Revision: 1.2 $

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

--union all	-- vaccinations
--select
--	vpv4i.pk_patient as pk_patient,
--	vpv4i.modified_when as modified_when,
--	vpv4i.date as clin_when,
--	coalesce (
--		(select short_alias from dem.staff where db_user = vpv4i.modified_by),
--		'<' || vpv4i.modified_by || '>'
--	) as modified_by,
--	'p' as soap_cat,
--	_('vaccine') || ': ' || vpv4i.vaccine || '; '
--		|| _('batch no') || ': ' || vpv4i.batch_no || '; '
--		|| _('indication') || ': ' || vpv4i.l10n_indication || '; '
--		|| _('site') || ': ' || vpv4i.site || '; '
--		|| _('notes') || ': ' || vpv4i.narrative || ';'
--	as narrative,
--	vpv4i.pk_encounter as pk_encounter,
--	vpv4i.pk_episode as pk_episode,
--	vpv4i.pk_health_issue as pk_health_issue,
--	vpv4i.pk_vaccination as src_pk,
--	'vaccination'::text as src_table
--from
--	clin.v_pat_vaccinations4indication vpv4i



--union all	-- lab requests
--select
--	vlr.pk_patient as pk_patient,
--	vlr.modified_when as modified_when,
--	vlr.sampled_when as clin_when,
--	coalesce (
--		(select short_alias from dem.staff where db_user = vlr.modified_by),
--		'<' || vlr.modified_by || '>'
--	) as modified_by,
--	vlr.soap_cat as soap_cat,
--	_('lab') || ': ' || vlr.lab_name || '; '
--		|| _('sample ID') || ': ' || vlr.request_id || '; '
--		|| _('sample taken') || ': ' || vlr.sampled_when || '; '
--		|| _('status') || ': ' || vlr.l10n_request_status || '; '
--		|| _('notes') || ': ' || coalesce(vlr.progress_note, '')
--		|| ' //'
--	as narrative,
--	vlr.pk_encounter as pk_encounter,
--	vlr.pk_episode as pk_epiode,
--	vlr.pk_health_issue as pk_health_issue,
--	vlr.pk_item as src_pk,
--	'clin.lab_request'::text as src_table
--from
--	clin.v_lab_requests vlr

;


comment on view clin.v_emr_journal is
	'Clinical patient data formatted into one string per
	 clinical entity even if it constains several user-
	 visible fields. Mainly useful for display as a simple
	 EMR journal.';


grant select on clin.v_emr_journal to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_emr_journal.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-clin-v_emr_journal.sql,v $
-- Revision 1.2  2008-10-12 15:00:20  ncq
-- - include allergy state
--
-- Revision 1.1  2008/09/02 15:41:19  ncq
-- - new
--
--
