-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_test_results cascade;

create view clin.v_test_results as
select
	cenc.fk_patient
		as pk_patient,
	c_tr.pk
		as pk_test_result,
	c_tr.clin_when,

	-- unified
	c_vtt.unified_abbrev,
	c_vtt.unified_name,
	c_vtt.unified_loinc,
	case when coalesce(trim(both from c_tr.val_alpha), '') = ''
		then c_tr.val_num::text
		else case when c_tr.val_num is null
			then c_tr.val_alpha
			else c_tr.val_num::text || ' (' || c_tr.val_alpha || ')'
		end
	end as unified_val,
	coalesce(c_tr.val_target_min, c_tr.val_normal_min)
		as unified_target_min,
	coalesce(c_tr.val_target_max, c_tr.val_normal_max)
		as unified_target_max,
	coalesce(c_tr.val_target_range, c_tr.val_normal_range)
		as unified_target_range,
	c_tr.status,
	c_tr.soap_cat,
	c_tr.narrative
		as comment,

	-- test result details
	c_tr.val_num,
	c_tr.val_alpha,
	c_tr.val_unit,
	c_vtt.reference_unit,
	c_tr.val_normal_min,
	c_tr.val_normal_max,
	c_tr.val_normal_range,
	c_tr.val_target_min,
	c_tr.val_target_max,
	c_tr.val_target_range,
	c_tr.abnormality_indicator,
	c_tr.norm_ref_group,
	c_tr.note_test_org,
	c_tr.material,
	c_tr.material_detail,

	-- test type details
	c_vtt.abbrev as abbrev_tt,
	c_vtt.name as name_tt,
	c_vtt.loinc as loinc_tt,
	c_vtt.comment_type as comment_tt,
	c_vtt.name_org as name_test_org,
	c_vtt.contact_org as contact_test_org,
	c_vtt.comment_org as comment_test_org,

	-- meta test type details
	c_vtt.is_fake_meta_type,
	c_vtt.abbrev_meta,
	c_vtt.name_meta,
	c_vtt.loinc_meta,
	c_vtt.comment_meta,

	-- episode/issue data
	epi.description
		as episode,
	chi.description
		as health_issue,

	-- status of last review
	coalesce(c_rtr.fk_reviewed_row, 0)::bool
		as reviewed,
	c_rtr.is_technically_abnormal
		as is_technically_abnormal,
	c_rtr.clinically_relevant
		as is_clinically_relevant,
	c_rtr.comment
		as review_comment,

	(select short_alias from dem.staff where pk = c_rtr.fk_reviewer)
		as last_reviewer,

	c_rtr.modified_when
		as last_reviewed,

	coalesce (
		(c_rtr.fk_reviewer = (select pk from dem.staff where db_user = current_user)),
		False
	)
		as review_by_you,

	coalesce (
		(c_tr.fk_intended_reviewer = c_rtr.fk_reviewer),
		False
	)
		as review_by_responsible_reviewer,

	-- potential review status
	(select short_alias from dem.staff where pk = c_tr.fk_intended_reviewer)
		as responsible_reviewer,

	coalesce (
		(c_tr.fk_intended_reviewer = (select pk from dem.staff where db_user = current_user)),
		False
	)
		as you_are_responsible,

	case when ((select 1 from dem.staff where db_user = c_tr.modified_by) is null)
		then '<' || c_tr.modified_by || '>'
		else (select short_alias from dem.staff where db_user = c_tr.modified_by)
	end
		as modified_by,

	c_tr.val_grouping,
	c_tr.source_data,

	c_tr.modified_when,
	c_tr.row_version as row_version,

	-- management keys
	-- clin.clin_root_item
	c_tr.pk_item,
	c_tr.fk_encounter as pk_encounter,
	c_tr.fk_episode as pk_episode,
	-- test_result
	c_tr.fk_type as pk_test_type,
	c_tr.fk_intended_reviewer as pk_intended_reviewer,
	c_tr.fk_request as pk_request,
	c_tr.xmin as xmin_test_result,
	-- v_unified_test_types
	c_vtt.pk_test_org,
	c_vtt.pk_meta_test_type,
	-- v_pat_episodes
	epi.fk_health_issue
		as pk_health_issue,
	-- reviewed_test_results
	c_rtr.fk_reviewer as pk_last_reviewer
from
	clin.test_result c_tr
		left join clin.encounter cenc on (c_tr.fk_encounter = cenc.pk)
		left join clin.reviewed_test_results c_rtr on (c_tr.pk = c_rtr.fk_reviewed_row)
		left join clin.v_test_types c_vtt on (c_tr.fk_type = c_vtt.pk_test_type)
		left join clin.episode epi on (c_tr.fk_episode = epi.pk)
			left join clin.health_issue chi on (epi.fk_health_issue = chi.pk)
;


comment on view clin.v_test_results is
	'denormalized view over test_results joined with (possibly unified) test
	 type and patient/episode/encounter keys';


grant select on clin.v_test_results to group "gm-doctors";
-- ==============================================================
select gm.log_script_insertion('v23-clin-v_test_results.sql', '23.0');
