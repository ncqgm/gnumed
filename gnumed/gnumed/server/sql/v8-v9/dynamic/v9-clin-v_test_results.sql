-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-v_test_results.sql,v 1.10 2008-08-15 15:59:39 ncq Exp $
-- $Revision: 1.10 $

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
	coalesce(tr.val_target_min, tr.val_normal_min)
		as unified_target_min,
	coalesce(tr.val_target_max, tr.val_normal_max)
		as unified_target_max,
	coalesce(tr.val_target_range, tr.val_normal_range)
		as unified_target_range,
	tr.soap_cat,
--	coalesce(tr.narrative, '') as comment,
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
	vpe.description as episode,
	vpe.health_issue,

	-- status of last review
	coalesce(rtr.fk_reviewed_row, 0)::bool
		as reviewed,
	rtr.is_technically_abnormal
		as is_technically_abnormal,
	rtr.clinically_relevant
		as is_clinically_relevant,
	rtr.comment
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
		as review_by_you,
	coalesce((tr.fk_intended_reviewer = rtr.fk_reviewer), False)
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
\unset ON_ERROR_STOP
drop view clin.v_test_results_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_test_results_journal as
select
	vtr.pk_patient
		as pk_patient,
	vtr.modified_when
		as modified_when,
	vtr.clin_when
		as clin_when,
	vtr.modified_by
		as modified_by,
	vtr.soap_cat
		as soap_cat,
	_('Test ')
		|| vtr.unified_code || ' ('
		|| vtr.unified_name || '): '
		|| vtr.unified_val::text || ' '
		|| coalesce(vtr.val_unit, '') || ' '
		|| coalesce('(' || vtr.abnormality_indicator || ')', '') || E'\n'
		|| _('Range: ')
			|| coalesce(vtr.unified_target_min::text, '') || ' - '
			|| coalesce(vtr.unified_target_max::text, '') || ' / '
			|| coalesce(vtr.unified_target_range, '')
			|| coalesce(' (' || vtr.norm_ref_group || ')', '') || E'\n'
		|| coalesce(_('Doc: ') || vtr.comment || E'\n', '')
		|| coalesce(_('MTA: ') || vtr.note_test_org || E'\n', '')
		|| coalesce (
			_('Review by ')
				|| vtr.last_reviewer || ' @ '
				|| to_char(vtr.last_reviewed, 'YYYY-MM-DD HH24:MI') || ': '
				|| case when vtr.is_technically_abnormal then _('abnormal') || ', ' else '' end
				|| case when vtr.is_clinically_relevant then _('relevant') || ' ' else '' end
				|| coalesce('(' || vtr.review_comment || E')\n', E'\n')
			, ''
		)
		|| _('Responsible clinician: ')
			|| vtr.responsible_reviewer || E'\n'
		|| _('Episode "')
			|| vtr.episode || '"'
			|| coalesce(_(' in health issue "') || vtr.health_issue || '"', '')
		as narrative,
	vtr.pk_encounter
		as pk_encounter,
	vtr.pk_episode
		as pk_episode,
	vtr.pk_health_issue
		as pk_health_issue,
	vtr.pk_test_result
		as src_pk,
	'clin.test_result'::text
		as src_table
from
	clin.v_test_results vtr
;


comment on view clin.v_test_results_journal is
	'formatting of v_test_results for inclusion in v_emr_journal';


grant select on clin.v_test_results_journal to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-v_test_results.sql,v $', '$Revision: 1.10 $');

-- ==============================================================
-- $Log: v9-clin-v_test_results.sql,v $
-- Revision 1.10  2008-08-15 15:59:39  ncq
-- - propagate row_version
--
-- Revision 1.9  2008/06/24 14:41:06  ncq
-- - improved formatting again, and made 8.1-proof
--
-- Revision 1.8  2008/06/24 14:04:23  ncq
-- - somewhat better journal formatting
--
-- Revision 1.7  2008/06/23 21:51:59  ncq
-- - stricter type casting
--
-- Revision 1.6  2008/06/22 17:34:33  ncq
-- - cleanup
-- - v_test_results_journal
--
-- Revision 1.5  2008/04/16 20:40:46  ncq
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