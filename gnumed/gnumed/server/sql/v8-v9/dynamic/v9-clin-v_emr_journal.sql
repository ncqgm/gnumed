-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten.Hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v9-clin-v_emr_journal.sql,v 1.1 2008-06-22 17:24:55 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop view clin.v_emr_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_emr_journal as

-- clin.clin_narrative
select
	vpi.pk_patient as pk_patient,
	cn.modified_when as modified_when,
	cn.clin_when as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cn.modified_by),
		'<' || cn.modified_by || '>'
	) as modified_by,
	cn.soap_cat as soap_cat,
	cn.narrative || ' //' as narrative,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	vpi.pk_health_issue as pk_health_issue,
	cn.pk as src_pk,
	'clin.clin_narrative'::text as src_table
from
	clin.v_pat_items vpi,
	clin.clin_narrative cn
where
	vpi.pk_item = cn.pk_item

union all	-- health issues
select
	chi.fk_patient as pk_patient,
	chi.modified_when as modified_when,
	chi.modified_when as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = chi.modified_by),
		'<' || chi.modified_by || '>'
	) as modified_by,
	'a' as soap_cat,
	_('health issue') || ': '
		|| chi.description
		|| coalesce((' (' || chi.laterality || ')'), '') || ', '
		|| _('noted at age') || ': '
		|| coalesce(chi.age_noted::text, '?') || ', '
		|| case when chi.is_active then _('active') else _('inactive') end || ', '
		|| case when chi.clinically_relevant then _('clinically relevant') else _('clinically not relevant') end
		|| case when chi.is_confidential then ', ' || _('confidential') else '' end
		|| case when chi.is_cause_of_death then ', ' || _('cause of death') else '' end
		|| ' //'
	as narrative,
	-1 as pk_encounter,
	-1 as pk_episode,
	chi.pk as pk_health_issue,
	chi.pk as src_pk,
	'clin.health_issue'::text as src_table
from
	clin.health_issue chi

union all	-- encounters
select
	cenc.fk_patient as pk_patient,
	cenc.modified_when as modified_when,
	-- FIXME: or last_affirmed ?
	cenc.started as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cenc.modified_by),
		'<' || cenc.modified_by || '>'
	) as modified_by,
	's' as soap_cat,
	_('encounter') || ': '
		|| (select _(description) from clin.encounter_type where pk=cenc.fk_type)
		|| to_char(cenc.started, ' YYYY-MM-DD HH24:MI') || to_char(cenc.last_affirmed, ' - HH24:MI') || '; '
		|| _('RFE') || ': ' || coalesce(cenc.reason_for_encounter, '?') || '; '
		|| _('AOE') || ': ' || coalesce(cenc.assessment_of_encounter, '?')
		|| ' //'
	as narrative,
	cenc.pk as pk_encounter,
	-1 as pk_episode,
	-1 as pk_health_issue,
	cenc.pk as src_pk,
	'clin.encounter'::text as src_table
from
	clin.encounter cenc

union all	-- episodes
select
	vpep.pk_patient as pk_patient,
	vpep.episode_modified_when as modified_when,
	vpep.episode_modified_when as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = vpep.episode_modified_by),
		'<' || vpep.episode_modified_by || '>'
	) as modified_by,
	's' as soap_cat,
	_('episode') || ': ' || vpep.description || ' //' as narrative,
	-1 as pk_encounter,
	vpep.pk_episode as pk_episode,
	-1 as pk_health_issue,
	vpep.pk_episode as src_pk,
	'clin.episode'::text as src_table
from
	clin.v_pat_episodes vpep

union all	-- family history
select
	vhxf.pk_patient as pk_patient,
	vhxf.modified_when as modified_when,
	vhxf.clin_when as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = vhxf.modified_by),
		'<' || vhxf.modified_by || '>'
	) as modified_by,
	vhxf.soap_cat as soap_cat,
	_('Family Hx') || ': '
		|| _(vhxf.relationship) || ' '
		|| vhxf.name_relative || ' @ '
		|| vhxf.age_noted || ': '
		|| vhxf.condition
		|| ' //'
	as narrative,
	vhxf.pk_encounter as pk_encounter,
	vhxf.pk_episode as pk_episode,
	vhxf.pk_health_issue as pk_health_issue,
	vhxf.pk_hx_family_item as src_pk,
	'clin.hx_family_item'::text as src_table
from
	clin.v_hx_family vhxf

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

union all	 -- allergies
select
	vpa.pk_patient as pk_patient,
	vpa.modified_when as modified_when,
	vpa.date as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = vpa.modified_by),
		'<' || vpa.modified_by || '>'
	) as modified_by,
	vpa.soap_cat as soap_cat,
	_('allergene') || ': ' || coalesce(vpa.allergene, '') || '; '
		|| _('substance') || ': ' || vpa.substance || '; '
		|| _('generic')   || ': ' || coalesce(vpa.generics, '') || '; '
		|| _('ATC code')  || ': ' || coalesce(vpa.atc_code, '') || '; '
		|| _('type')      || ': ' || vpa.l10n_type || '; '
		|| _('reaction')  || ': ' || coalesce(vpa.reaction, '')
		|| ' //'
	as narrative,
	vpa.pk_encounter as pk_encounter,
	vpa.pk_episode as pk_episode,
	vpa.pk_health_issue as pk_health_issue,
	vpa.pk_allergy as src_pk,
	'clin.allergy' as src_table
from
	clin.v_pat_allergies vpa

union all	-- lab requests
select
	vlr.pk_patient as pk_patient,
	vlr.modified_when as modified_when,
	vlr.sampled_when as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = vlr.modified_by),
		'<' || vlr.modified_by || '>'
	) as modified_by,
	vlr.soap_cat as soap_cat,
	_('lab') || ': ' || vlr.lab_name || '; '
		|| _('sample ID') || ': ' || vlr.request_id || '; '
		|| _('sample taken') || ': ' || vlr.sampled_when || '; '
		|| _('status') || ': ' || vlr.l10n_request_status || '; '
		|| _('notes') || ': ' || coalesce(vlr.progress_note, '')
		|| ' //'
	as narrative,
	vlr.pk_encounter as pk_encounter,
	vlr.pk_episode as pk_epiode,
	vlr.pk_health_issue as pk_health_issue,
	vlr.pk_item as src_pk,
	'lab_request' as src_table
from
	clin.v_lab_requests vlr

union all	-- test results
select * from clin.v_test_results_journal

union all	-- documents
select
	vdm.pk_patient as pk_patient,
	vdm.modified_when as modified_when,
	vdm.date as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = vdm.modified_by),
		'<' || vdm.modified_by || '>'
	) as modified_by,
	'o' as soap_cat,
	_('document entry') || ': '
		|| vdm.l10n_type || ' "'
		|| vdm.ext_ref || '" ('
		|| to_char(vdm.date, 'YYYY-MM-DD HH24:MI') || '): '
		|| coalesce(vdm.comment, '')
		|| ' //'
	as narrative,
	vdm.pk_encounter as pk_encounter,
	vdm.pk_episode as pk_episode,
	vdm.pk_health_issue as pk_health_issue,
	vdm.pk_doc as src_pk,
	'blobs.doc_med' as src_table
from
	blobs.v_doc_med vdm

;


comment on view clin.v_emr_journal is
	'Clinical patient data formatted into one string per
	 clinical entity even if it constains several user-
	 visible fields. Mainly useful for display as a simple
	 EMR journal.';


grant select on clin.v_emr_journal to group "gm-doctors";


select i18n.i18n('document entry');
select i18n.i18n('Family Hx');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-v_emr_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-v_emr_journal.sql,v $
-- Revision 1.1  2008-06-22 17:24:55  ncq
-- - recreate
--
-- Revision 1.3  2007/06/12 13:23:58  ncq
-- - improved output
-- - mark strings for translation
--
-- Revision 1.2  2007/06/11 20:02:07  ncq
-- - set proper sOap category on document entries
--
-- Revision 1.1  2007/06/11 18:41:31  ncq
-- - new
--
-- Revision 1.2  2006/12/11 17:03:58  ncq
-- - dem.v_staff -> dem.staff
--
-- Revision 1.1  2006/11/07 15:18:38  ncq
-- - improved
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
