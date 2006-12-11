-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - enhance narrative search view
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-v_narrative4search.sql,v 1.3 2006-12-11 17:03:58 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_narrative4search cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- FIXME: add form_data
create view clin.v_narrative4search as


select	-- clin.clin_root_items
	vpi.pk_patient as pk_patient,
	vpi.soap_cat as soap_cat,
	vpi.narrative as narrative,
	vpi.pk_encounter as pk_encounter,
	vpi.pk_episode as pk_episode,
	vpi.pk_health_issue as pk_health_issue,
	vpi.pk_item as src_pk,
	vpi.src_table as src_table
from
	clin.v_pat_items vpi
where
	trim(coalesce(vpi.narrative, '')) != ''


union all	-- health issues
select
	chi.fk_patient as pk_patient,
	'a' as soap_cat,
	chi.description as narrative,
	null as pk_encounter,
	null as pk_episode,
	chi.pk as pk_health_issue,
	chi.pk as src_pk,
	'clin.health_issue' as src_table
from
	clin.health_issue chi
where
	trim(coalesce(chi.description, '')) != ''


union all	-- encounters
select
	cenc.fk_patient as pk_patient,
	's' as soap_cat,
	(coalesce(cenc.reason_for_encounter, '') || '; ' ||
	 coalesce(cenc.assessment_of_encounter, '')
	) as narrative,
	cenc.pk as pk_encounter,
	null as pk_episode,
	null as pk_health_issue,
	cenc.pk as src_pk,
	'clin.encounter' as src_table
from
	clin.encounter cenc
where
	trim(coalesce(cenc.reason_for_encounter, '')) != '' or
	trim(coalesce(cenc.assessment_of_encounter, '')) != ''


union all	-- episodes
select
	vpep.pk_patient as pk_patient,
	's' as soap_cat,
	vpep.description as narrative,
	null as pk_encounter,
	vpep.pk_episode as pk_episode,
	vpep.pk_health_issue as pk_health_issue,
	vpep.pk_episode as src_pk,
	'clin.episode' as src_table
from
	clin.v_pat_episodes vpep


union all	-- family history
select
	vhxf.pk_patient as pk_patient,
	vhxf.soap_cat as soap_cat,
	(_(vhxf.relationship) || ' (' ||
	 vhxf.relationship || ') ' ||
	 vhxf.name_relative || ': ' ||
	 vhxf.condition
	) as narrative,
	vhxf.pk_encounter as pk_encounter,
	vhxf.pk_episode as pk_episode,
	vhxf.pk_health_issue as pk_health_issue,
	vhxf.pk_hx_family_item as src_pk,
	'clin.hx_family_item' as src_table
from
	clin.v_hx_family vhxf


union all	-- documents
select
	vdm.pk_patient as pk_patient,
	'o' as soap_cat,
	(vdm.type || ' ' ||
	 vdm.l10n_type || ' ' ||
	 coalesce(vdm.ext_ref, '') || ' ' ||
	 coalesce(vdm.comment, '')
	) as narrative,
	vdm.pk_encounter as pk_encounter,
	vdm.pk_episode as pk_episode,
	vdm.pk_health_issue as pk_health_issue,
	vdm.pk_doc as src_pk,
	'blobs.doc_med' as src_table
from
	blobs.v_doc_med vdm


union all	-- document objects
select
	vo4d.pk_patient as pk_patient,
	'o' as soap_cat,
	vo4d.obj_comment as narrative,
	vo4d.pk_encounter as pk_encounter,
	vo4d.pk_episode as pk_episode,
	vo4d.pk_health_issue as pk_health_issue,
	vo4d.pk_obj as src_pk,
	'blobs.doc_obj' as src_table
from
	blobs.v_obj4doc_no_data vo4d
where
	trim(coalesce(vo4d.obj_comment, '')) != ''


union all	-- document descriptions
select
	vdd.pk_patient as pk_patient,
	'o' as soap_cat,
	vdd.description as narrative,
	vdd.pk_encounter as pk_encounter,
	vdd.pk_episode as pk_episode,
	vdd.pk_health_issue as pk_health_issue,
	vdd.pk_doc_desc as src_pk,
	'blobs.doc_desc' as src_table
from
	blobs.v_doc_desc vdd
where
	trim(coalesce(vdd.description, '')) != ''


union all	-- reviewed documents
select
	vrdo.pk_patient as pk_patient,
	's' as soap_cat,
	vrdo.comment as narrative,
	null as pk_encounter,
	vrdo.pk_episode as pk_episode,
	vrdo.pk_health_issue as pk_health_issue,
	vrdo.pk_review_root as src_pk,
	'blobs.v_reviewed_doc_objects' as src_table
from
	blobs.v_reviewed_doc_objects vrdo
where
	trim(coalesce(vrdo.comment, '')) != ''

;

-- --------------------------------------------------------------
comment on view clin.v_narrative4search is
	'unformatted *complete* narrative for patients
	 including health issue/episode/encounter descriptions,
	 mainly for searching the narrative';

-- --------------------------------------------------------------
grant select on clin.v_narrative4search to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-v_narrative4search.sql,v $', '$Revision: 1.3 $');

commit;

-- ==============================================================
-- $Log: clin-v_narrative4search.sql,v $
-- Revision 1.3  2006-12-11 17:03:58  ncq
-- - dem.v_staff -> dem.staff
--
-- Revision 1.2  2006/10/24 13:10:30  ncq
-- - health issue id_patient -> fk_patient
--
-- Revision 1.1  2006/09/25 10:55:01  ncq
-- - added here
--
-- Revision 1.2  2006/09/18 17:32:26  ncq
-- - exclude empty encounters
--
-- Revision 1.1  2006/09/16 21:46:57  ncq
-- - include FKs for narrative search
-- - include BLOB tables
-- - UNION ALL
-- - various coalesce fixes
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
