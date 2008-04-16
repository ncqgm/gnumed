-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-v_test_results.sql,v 1.5 2008-04-16 20:40:46 ncq Exp $
-- $Revision: 1.5 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_test_results cascade;
\set ON_ERROR_STOP 1


create view clin.v_test_results as
select
	-- v_pat_episodes
	vpe.pk_patient as pk_patient,
	-- test_result
	tr.pk as pk_test_result,
	-- unified
	tr.clin_when,
	vttu.unified_code,
	vttu.unified_name,
	case when coalesce(trim(both from tr.val_alpha), '') = ''
		then tr.val_num::text
		else case when tr.val_num is null
			then tr.val_alpha
			else tr.val_num::text || ' (' || tr.val_alpha || ')'
		end
	end as unified_val,
	case when tr.val_target_min is null
		then tr.val_normal_min
		else tr.val_target_min
	end as unified_target_min,
	case when tr.val_target_max is null
		then tr.val_normal_max
		else tr.val_target_max
	end as unified_target_max,
	case when tr.val_target_range is null
		then tr.val_normal_range
		else tr.val_target_range
	end as unified_target_range,
	tr.soap_cat,
	coalesce(tr.narrative, '') as comment,
	-- test result data
	tr.val_num,
	tr.val_alpha,
	tr.val_unit,
	vttu.conversion_unit,
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
	-- test type data
	vttu.code_tt,
	vttu.name_tt,
	vttu.coding_system_tt,
	vttu.comment_tt,
	vttu.code_unified,
	vttu.name_unified,
	vttu.coding_system_unified,
	vttu.comment_unified,
	-- episode/issue data
	vpe.description as episode,
	vpe.health_issue,

	-- status of last review
	coalesce(rtr.fk_reviewed_row, 0)::bool
--	exists(select 1 from clin.reviewed_test_results where fk_reviewed_row = tr.pk)
		as reviewed,

	rtr.is_technically_abnormal
--	(select is_technically_abnormal
--	 from clin.reviewed_test_results
--	 where fk_reviewed_row = tr.pk
--	)
		as is_technically_abnormal,

	rtr.clinically_relevant
--	(select clinically_relevant
--	 from clin.reviewed_test_results
--	 where fk_reviewed_row = tr.pk
--	)
		as is_clinically_relevant,

	rtr.comment
--	(select comment
--	 from clin.reviewed_test_results
--	 where
--		fk_reviewed_row = tr.pk
--	)
		as review_comment,

	(select
		short_alias || ' (' ||
		coalesce(title || ' ', '') ||
		coalesce(firstnames || ' ', '') ||
		coalesce(lastnames, '') ||
		')'
	 from dem.v_staff
	 where pk_staff = rtr.fk_reviewer
	) as last_reviewer,

	rtr.modified_when
		as last_reviewed,

	coalesce((rtr.fk_reviewer = (select pk from dem.staff where db_user = current_user)), False)
--	(select exists (
--		select 1 from clin.reviewed_test_results
--		where
--			fk_reviewed_row = tr.pk and
--			fk_reviewer = (select pk from dem.staff where db_user = current_user)
--	))
		as review_by_you,

	coalesce((tr.fk_intended_reviewer = rtr.fk_reviewer), False)
--	(select exists (
--		select 1 from clin.reviewed_test_results
--		where
--			fk_reviewed_row = tr.pk and
--			fk_reviewer = tr.fk_intended_reviewer
--	))
		as review_by_responsible_reviewer,

	-- potential review status
	(select
		short_alias || ' (' ||
		coalesce(title || ' ', '') ||
		coalesce(firstnames || ' ', '') ||
		coalesce(lastnames, '') ||
		')'
	 from dem.v_staff
	 where pk_staff = tr.fk_intended_reviewer
	) as responsible_reviewer,

	coalesce (
		(tr.fk_intended_reviewer = (select pk from dem.staff where db_user = current_user)),
		False
	) as you_are_responsible,

	case when ((select 1 from dem.v_staff where db_user = tr.modified_by) is null)
		then '<' || tr.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = tr.modified_by)
	end as modified_by,

	tr.modified_when,

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
	vttu.pk_test_org,
	vttu.pk_test_type_unified,
	-- v_pat_episodes
	vpe.pk_health_issue,
	-- reviewed_test_results
	rtr.fk_reviewer as pk_last_reviewer
from
	clin.test_result tr left join clin.reviewed_test_results rtr on (tr.pk = rtr.fk_reviewed_row),
	clin.v_unified_test_types vttu,
	clin.v_pat_episodes vpe
where
	vttu.pk_test_type = tr.fk_type
		and
	tr.fk_episode = vpe.pk_episode
;


comment on view clin.v_test_results is
	'denormalized view over test_results joined with (possibly unified) test
	 type and patient/episode/encounter keys';


grant select on clin.v_test_results to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-v_test_results.sql,v $', '$Revision: 1.5 $');

-- ==============================================================
-- $Log: v9-clin-v_test_results.sql,v $
-- Revision 1.5  2008-04-16 20:40:46  ncq
-- - do proper join on clin.reviewed_test_results
-- - support one-review-per-row paradigm
--
-- Revision 1.4  2008/04/14 17:15:41  ncq
-- - notification setup moved away
-- - only one review per row of results so support that
--
-- Revision 1.3  2008/04/02 10:17:54  ncq
-- - cleanup
-- - add you_are_reviewer
--
-- Revision 1.2  2008/03/29 16:25:49  ncq
-- - align column names
-- - cleanup
--
-- Revision 1.1  2008/03/20 15:27:28  ncq
-- - add episode/issue/review status
--
-- Revision 1.1  2008/01/27 21:06:00  ncq
-- - new
-- 