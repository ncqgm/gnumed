-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_test_results_journal cascade;


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
		as row_version,

	-- issue
	c_vtr.health_issue
		as health_issue,
	c_hi.laterality
		as issue_laterality,
	c_hi.is_active
		as issue_active,
	c_hi.clinically_relevant
		as issue_clinically_relevant,
	c_hi.is_confidential
		as issue_confidential,

	-- episode
	c_vtr.episode
		as episode,
	c_epi.is_open
		as episode_open,

	-- encounter
	c_enc.started
		as encounter_started,
	c_enc.last_affirmed
		as encounter_last_affirmed,
	c_ety.description
		as encounter_type,
	_(c_ety.description)
		as encounter_l10n_type

from
	clin.v_test_results c_vtr
		inner join clin.encounter c_enc on (c_vtr.pk_encounter = c_enc.pk)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
				inner join clin.episode c_epi on (c_vtr.pk_episode = c_epi.pk)
					left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
;


comment on view clin.v_test_results_journal is
	'formatting of v_test_results for inclusion in v_emr_journal';


grant select on clin.v_test_results_journal to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_test_results_journal.sql', '22.0');
