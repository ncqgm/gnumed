-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_narrative4search cascade;

create view clin.v_narrative4search as

select * from (

	-- clin.clin_root_items
	select
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
		src_table not in (
			'clin.allergy',
			'clin.test_result',
			'clin.procedure',
			'clin.intake',
			'clin.intake_regimen',
			'clin.family_history',
			'clin.intake'
		)

	union all
		select * from clin.v_intake4narr_search
		where gm.is_null_or_blank_string(narrative) is FALSE


	union all
		select * from clin.v_intake_regimen4narr_search
		where gm.is_null_or_blank_string(narrative) is FALSE


	union all
	select		-- clin.procedure
		(select fk_patient from clin.encounter where pk = cpr.fk_encounter)
			as pk_patient,
		cpr.soap_cat
			as soap_cat,
		cpr.narrative
			as narrative,
		cpr.fk_encounter
			as pk_encounter,
		cpr.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = cpr.fk_episode)
			as pk_health_issue,
		cpr.pk
			as src_pk,
		'clin.procedure'
			as src_table
	from
		clin.procedure cpr
	where
		cpr.narrative is not NULL


	union all
	select		-- test results
		(select fk_patient from clin.encounter where pk = ctr.fk_encounter)
			as pk_patient,
		ctr.soap_cat
			as soap_cat,
		coalesce(ctr.narrative, '')
			|| coalesce(' ' || ctr.val_alpha, '')
			|| coalesce(' ' || ctr.val_unit, '')
			|| coalesce(' ' || ctr.val_normal_range, '')
			|| coalesce(' ' || ctr.val_target_range, '')
			|| coalesce(' ' || ctr.norm_ref_group, '')
			|| coalesce(' ' || ctr.note_test_org, '')
			|| coalesce(' ' || ctr.material, '')
			|| coalesce(' ' || ctr.material_detail, '')
			as narrative,
		ctr.fk_encounter
			as pk_encounter,
		ctr.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = ctr.fk_episode)
			as pk_health_issue,
		ctr.pk
			as src_pk,
		'clin.test_result'
			as src_table
	from
		clin.test_result ctr


	union all	-- test result reviews
	select
		(select fk_patient from clin.encounter where pk =
			(select fk_encounter from clin.test_result where clin.test_result.pk = crtr.fk_reviewed_row)
		)
			as pk_patient,
		'o'::text
			as soap_cat,
		crtr.comment
			as narrative,
		(select fk_encounter from clin.test_result where clin.test_result.pk = crtr.fk_reviewed_row)
			as pk_encounter,
		(select fk_episode from clin.test_result where clin.test_result.pk = crtr.fk_reviewed_row)
			as pk_episode,
		(select fk_health_issue from clin.episode where pk =
			(select fk_episode from clin.test_result where clin.test_result.pk = crtr.fk_reviewed_row)
		)
			as pk_health_issue,
		crtr.pk
			as src_pk,
		'clin.reviewed_test_results'
			as src_table
	from
		clin.reviewed_test_results crtr


	union all
	select -- allergy state
		(select fk_patient from clin.encounter where pk = cas.fk_encounter)
			as pk_patient,
		'o'::text
			as soap_cat,
		cas.comment
			as narrative,
		cas.fk_encounter
			as pk_encounter,
		null
			as pk_episode,
		null
			as pk_health_issue,
		cas.pk
			as src_pk,
		'clin.allergy_state'
			as src_table
	from
		clin.allergy_state cas
	where
		cas.comment is not NULL


	union all
	select -- allergies
		(select fk_patient from clin.encounter where pk = ca.fk_encounter)
			as pk_patient,
		ca.soap_cat
			as soap_cat,
		coalesce(narrative, '')
			|| coalesce(' ' || substance, '')
			|| coalesce(' ' || substance_code, '')
			|| coalesce(' ' || generics, '')
			|| coalesce(' ' || allergene, '')
			|| coalesce(' ' || atc_code, '')
			as narrative,
		ca.fk_encounter
			as pk_encounter,
		ca.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = ca.fk_episode)
			as pk_health_issue,
		ca.pk
			as src_pk,
		'clin.allergy'
			as src_table
	from
		clin.allergy ca


	union all	-- health issues
	select
		(select fk_patient from clin.encounter where pk = chi.fk_encounter)
			as pk_patient,
		'a' as soap_cat,
		chi.description
			|| coalesce(' ' || chi.summary, '')
			as narrative,
		chi.fk_encounter
			as pk_encounter,
		null
			as pk_episode,
		chi.pk
			as pk_health_issue,
		chi.pk
			as src_pk,
		'clin.health_issue'
			as src_table
	from
		clin.health_issue chi


	union all	-- encounters
	select
		cenc.fk_patient as pk_patient,
		's' as soap_cat,
		coalesce(cenc.reason_for_encounter, '')
			|| coalesce(' ' || cenc.assessment_of_encounter, '')
			as narrative,
		cenc.pk as pk_encounter,
		null as pk_episode,
		null as pk_health_issue,
		cenc.pk as src_pk,
		'clin.encounter' as src_table
	from
		clin.encounter cenc


	union all	-- episodes
	select
		(select fk_patient from clin.encounter where pk = cep.fk_encounter)
			as pk_patient,
		's' as soap_cat,
		cep.description
			|| coalesce(' ' || cep.summary, '')
			as narrative,
		cep.fk_encounter
			as pk_encounter,
		cep.pk
			as pk_episode,
		cep.fk_health_issue
			as pk_health_issue,
		cep.pk
			as src_pk,
		'clin.episode'
			as src_table
	from
		clin.episode cep


	union all	-- family history
	select
		c_vfhx.pk_patient,
		c_vfhx.soap_cat,
		(c_vfhx.relation || ' / ' || c_vfhx.l10n_relation || ' '
		 || c_vfhx.name_relative || ': '
		 || c_vfhx.condition
		) as narrative,
		c_vfhx.pk_encounter,
		c_vfhx.pk_episode,
		c_vfhx.pk_health_issue,
		c_vfhx.pk_family_history as src_pk,
		'clin.family_history' as src_table
	from
		clin.v_family_history c_vfhx


	union all	-- documents
	select
		vdm.pk_patient as pk_patient,
		'o' as soap_cat,
		(vdm.l10n_type || ' ' ||
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


	union all	-- patient tags
	select
		d_vit.pk_identity
			as pk_patient,
		's' as soap_cat,
		d_vit.l10n_description
			|| coalesce(' ' || d_vit.comment, '')
			as narrative,
		null
			as pk_encounter,
		null
			as pk_episode,
		null
			as pk_health_issue,
		d_vit.pk_identity_tag
			as src_pk,
		'dem.v_identity_tags'
			as src_table
	from
		dem.v_identity_tags d_vit


	union all	-- external care
	select
		c_vec.pk_identity
			as pk_patient,
		's' as soap_cat,
		case
			when c_vec.pk_health_issue is null then
				coalesce(c_vec.issue, '')
				|| coalesce(' / ' || c_vec.provider, '')
				|| coalesce(' / ' || c_vec.comment, '')
			else
				coalesce(c_vec.provider, '')
				|| coalesce(' / ' || c_vec.comment, '')
		end as narrative,
		c_vec.pk_encounter
			as pk_encounter,
		null
			as pk_episode,
		c_vec.pk_health_issue
			as pk_health_issue,
		c_vec.pk_external_care
			as src_pk,
		'clin.v_external_care'
			as src_table
	from
		clin.v_external_care c_vec


	union all	-- export items
	select
		c_vei.pk_identity
			as pk_patient,
		's' as soap_cat,
		case
			when c_vei.pk_doc_obj is null then
				coalesce(c_vei.description, '')
				|| coalesce(' / ' || c_vei.filename, '')
			else
				coalesce(c_vei.description, '')
		end as narrative,
		null
			as pk_encounter,
		null
			as pk_episode,
		null
			as pk_health_issue,
		c_vei.pk_export_item
			as src_pk,
		'clin.v_export_items'
			as src_table
	from
		clin.v_export_items c_vei


	union all	-- hint suppression rationale
	select
		(select fk_patient from clin.encounter where pk = c_sh.fk_encounter)
			as pk_patient,
		'p' as soap_cat,
		c_sh.rationale
			as narrative,
		c_sh.fk_encounter
			as pk_encounter,
		null
			as pk_episode,
		null
			as pk_health_issue,
		c_sh.pk
			as src_pk,
		'clin.suppressed_hint'
			as src_table
	from
		clin.suppressed_hint c_sh


	-- add in demographics ----------------
	union all	-- tags on patients
	SELECT
		d_it.fk_identity
			AS pk_patient,
		'u' AS soap_cat,
		d_it.comment
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_it.pk
			AS src_pk,
		'dem.identity_tag'
			AS src_table
	FROM
		dem.identity_tag d_it


	union all	-- job description
	SELECT
		d_lj2p.fk_identity
			AS pk_patient,
		'u' AS soap_cat,
		d_lj2p.activities
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_lj2p.pk
			AS src_pk,
		'dem.lnk_job2person'
			AS src_table
	FROM
		dem.lnk_job2person d_lj2p


	union all	-- comm channel comment
	SELECT
		d_li2c.fk_identity
			AS pk_patient,
		'u' AS soap_cat,
		d_li2c.comment
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_li2c.pk
			AS src_pk,
		'dem.lnk_identity2comm'
			AS src_table
	FROM
		dem.lnk_identity2comm d_li2c


	union all	-- external ID comment
	SELECT
		d_li2e.id_identity
			AS pk_patient,
		'u' AS soap_cat,
		d_li2e.comment
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_li2e.id
			AS src_pk,
		'dem.lnk_identity2ext_id'
			AS src_table
	FROM
		dem.lnk_identity2ext_id d_li2e


	union all	-- message inbox comment
	SELECT
		d_mi.fk_patient
			AS pk_patient,
		'u' AS soap_cat,
		d_mi.comment
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_mi.pk
			AS src_pk,
		'dem.message_inbox'
			AS src_table
	FROM
		dem.message_inbox d_mi
	-- end demographics data --------------

) as union_table

where
	trim(coalesce(union_table.narrative, '')) != ''
;


comment on view clin.v_narrative4search is
	'unformatted *complete* narrative for patients
	 including health issue/episode/encounter descriptions,
	 extended by some demographic comment bits (not demographics itself),
	 mainly for searching the narrative in context';


grant select on clin.v_narrative4search to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_narrative4search.sql', '23.0');
