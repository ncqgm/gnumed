-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_test_results_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_test_results_journal as
select
	c_vtr.pk_patient
		as pk_patient,
	c_vtr.modified_when
		as modified_when,
	c_vtr.clin_when
		as clin_when,
	c_vtr.modified_by
		as modified_by,
	c_vtr.soap_cat
		as soap_cat,
	coalesce ((
		c_vtr.unified_name || ' ('
		|| c_vtr.unified_abbrev
		|| coalesce(' [#' || c_vtr.unified_loinc || ']', '') || '): '
		|| c_vtr.unified_val::text || ' '
		|| coalesce(c_vtr.val_unit, '') || ' '
		|| coalesce('(' || c_vtr.abnormality_indicator || ')', '') || E'\n'
		|| _('Range: ')
			|| coalesce(c_vtr.unified_target_min::text, '') || ' - '
			|| coalesce(c_vtr.unified_target_max::text, '') || ' / '
			|| coalesce(c_vtr.unified_target_range, '')
			|| coalesce(' (' || c_vtr.norm_ref_group || ')', '') || E'\n'
		|| coalesce(_('Assessment: ') || c_vtr.comment || E'\n', '')
		|| coalesce(_('Context: ') || c_vtr.note_test_org || E'\n', '')
		|| coalesce(_('Status: ') || c_vtr.status || E'\n', '')
		|| coalesce(_('Grouping: ') || c_vtr.val_grouping || E'\n', '')
		|| coalesce (
			_('Review by ')
				|| c_vtr.last_reviewer || ' @ '
				|| to_char(c_vtr.last_reviewed, 'YYYY-MM-DD HH24:MI') || ': '
				|| case when c_vtr.is_technically_abnormal then _('abnormal') || ', ' else '' end
				|| case when c_vtr.is_clinically_relevant then _('relevant') || ' ' else '' end
				|| coalesce('(' || c_vtr.review_comment || E')\n', E'\n')
			, ''
		)
		|| _('Responsible clinician: ')
			|| c_vtr.responsible_reviewer
		|| coalesce(_('Source data:') || E'\n' || c_vtr.source_data || E'\n', '')
		), 'faulty clin.v_test_results_journal definition'
	)	as narrative,
	c_vtr.pk_encounter
		as pk_encounter,
	c_vtr.pk_episode
		as pk_episode,
	c_vtr.pk_health_issue
		as pk_health_issue,
	c_vtr.pk_test_result
		as src_pk,
	'clin.test_result'::text
		as src_table,
	c_vtr.row_version
		as row_version
from
	clin.v_test_results c_vtr
;


comment on view clin.v_test_results_journal is
	'formatting of v_test_results for inclusion in v_emr_journal';


grant select on clin.v_test_results_journal to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-v_test_results_journal.sql', '20.0');
