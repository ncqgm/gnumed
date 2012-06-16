-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v13-clin-v_test_results.sql,v 1.1 2010-02-02 13:42:03 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;


-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_test_results cascade;
\set ON_ERROR_STOP 1


create view clin.v_test_results as

select
	cenc.fk_patient
		as pk_patient,
	tr.pk
		as pk_test_result,
	tr.clin_when,

	-- unified
	vutt.unified_abbrev,
	vutt.unified_name,
	vutt.unified_loinc,
	case when coalesce(trim(both from tr.val_alpha), '') = ''
		then tr.val_num::text
		else case when tr.val_num is null
			then tr.val_alpha
			else tr.val_num::text || ' (' || tr.val_alpha || ')'
		end
	end as unified_val,
	coalesce(tr.val_target_min, tr.val_normal_min)
		as unified_target_min,
	coalesce(tr.val_target_max, tr.val_normal_max)
		as unified_target_max,
	coalesce(tr.val_target_range, tr.val_normal_range)
		as unified_target_range,
	tr.soap_cat,
	tr.narrative
		as comment,

	-- test result details
	tr.val_num,
	tr.val_alpha,
	tr.val_unit,
	vutt.conversion_unit,
	tr.val_normal_min,
	tr.val_normal_max,
	tr.val_normal_range,
	tr.val_target_min,
	tr.val_target_max,
	tr.val_target_range,
	tr.abnormality_indicator,
	tr.norm_ref_group,
	tr.note_test_org,
	tr.material,
	tr.material_detail,

	-- test type details
	vutt.abbrev_tt,
	vutt.name_tt,
	vutt.loinc_tt,
	vutt.code_tt,
	vutt.coding_system_tt,
	vutt.comment_tt,
	cto.internal_name as name_test_org,
	cto.contact as contact_test_org,

	-- meta test type details
	vutt.abbrev_meta,
	vutt.name_meta,
	vutt.loinc_meta,
	vutt.comment_meta,

	-- episode/issue data
	epi.description
		as episode,
	chi.description
		as health_issue,

	-- status of last review
	coalesce(rtr.fk_reviewed_row, 0)::bool
		as reviewed,
	rtr.is_technically_abnormal
		as is_technically_abnormal,
	rtr.clinically_relevant
		as is_clinically_relevant,
	rtr.comment
		as review_comment,

	(select short_alias from dem.staff where pk = rtr.fk_reviewer)
		as last_reviewer,

	rtr.modified_when
		as last_reviewed,

	coalesce (
		(rtr.fk_reviewer = (select pk from dem.staff where db_user = current_user)),
		False
	)
		as review_by_you,

	coalesce (
		(tr.fk_intended_reviewer = rtr.fk_reviewer),
		False
	)
		as review_by_responsible_reviewer,

	-- potential review status
	(select short_alias from dem.staff where pk = tr.fk_intended_reviewer)
		as responsible_reviewer,

	coalesce (
		(tr.fk_intended_reviewer = (select pk from dem.staff where db_user = current_user)),
		False
	)
		as you_are_responsible,

	case when ((select 1 from dem.staff where db_user = tr.modified_by) is null)
		then '<' || tr.modified_by || '>'
		else (select short_alias from dem.staff where db_user = tr.modified_by)
	end
		as modified_by,

	tr.modified_when,
	tr.row_version as row_version,

	-- management keys
	-- clin.clin_root_item
	tr.pk_item,
	tr.fk_encounter as pk_encounter,
	tr.fk_episode as pk_episode,
	-- test_result
	tr.fk_type as pk_test_type,
	tr.fk_intended_reviewer as pk_intended_reviewer,
	tr.xmin as xmin_test_result,
	-- v_unified_test_types
	vutt.pk_test_org,
	vutt.pk_meta_test_type,
	-- v_pat_episodes
	epi.fk_health_issue
		as pk_health_issue,
	-- reviewed_test_results
	rtr.fk_reviewer as pk_last_reviewer
from
	clin.test_result tr
		left join clin.encounter cenc on (tr.fk_encounter = cenc.pk)
			left join clin.episode epi on (tr.fk_episode = epi.pk)
				left join clin.reviewed_test_results rtr on (tr.pk = rtr.fk_reviewed_row)
					left join clin.health_issue chi on (epi.fk_health_issue = chi.pk)
	,
	clin.v_unified_test_types vutt
		left join clin.test_org cto on (vutt.pk_test_org = cto.pk)
where
	tr.fk_type = vutt.pk_test_type
;


comment on view clin.v_test_results is
	'denormalized view over test_results joined with (possibly unified) test
	 type and patient/episode/encounter keys';


grant select on clin.v_test_results to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-clin-v_test_results.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v13-clin-v_test_results.sql,v $
-- Revision 1.1  2010-02-02 13:42:03  ncq
-- - include lab name/contact
--
--