-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_test_results_journal.sql,v 1.1 2008-09-02 15:41:21 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

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
select gm.log_script_insertion('$RCSfile: v10-clin-v_test_results_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_test_results_journal.sql,v $
-- Revision 1.1  2008-09-02 15:41:21  ncq
-- - new
--
--