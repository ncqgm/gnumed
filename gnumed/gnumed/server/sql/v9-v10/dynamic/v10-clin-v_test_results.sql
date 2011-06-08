-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_test_results.sql,v 1.4 2009-05-22 10:56:25 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_test_result_fk_type cascade;
\set ON_ERROR_STOP 1

create index idx_test_result_fk_type on clin.test_result(fk_type);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_rtr_fk_reviewer cascade;
\set ON_ERROR_STOP 1

create index idx_rtr_fk_reviewer on clin.reviewed_test_results(fk_reviewer);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_ltt2ut_fk_ttu cascade;
\set ON_ERROR_STOP 1

create index idx_ltt2ut_fk_ttu on clin.lnk_ttype2unified_type(fk_test_type_unified);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_test_results cascade;
\set ON_ERROR_STOP 1


create view clin.v_test_results as

select
	cenc.fk_patient
		as pk_patient,
	-- test_result
	tr.pk as pk_test_result,
	tr.clin_when,
	-- unified
	vttu.unified_code,
	vttu.unified_name,
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
	vttu.pk_test_org,
	vttu.pk_test_type_unified,
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
	clin.v_unified_test_types vttu
where
	tr.fk_type = vttu.pk_test_type
;


comment on view clin.v_test_results is
	'denormalized view over test_results joined with (possibly unified) test
	 type and patient/episode/encounter keys';


grant select on clin.v_test_results to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_test_results.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: v10-clin-v_test_results.sql,v $
-- Revision 1.4  2009-05-22 10:56:25  ncq
-- - comment out readonly cmd
--
-- Revision 1.3  2009/01/28 11:29:30  ncq
-- - improved query speed as per list discussion with Tom Lane et al
--
-- Revision 1.2  2009/01/27 11:42:08  ncq
-- - add indexe
-- - give the planner better chances at optimizing joins
--
-- Revision 1.1  2008/09/02 15:41:21  ncq
-- - new
--
--