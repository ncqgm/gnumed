-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_suppressed_hints_journal cascade;


create view clin.v_suppressed_hints_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_sh.modified_when
		as modified_when,
	c_sh.suppressed_when
		as clin_when,
	c_sh.modified_by
		as modified_by,
	'p'::text
		as soap_cat,
	case
		when r_vah.is_active is TRUE then
			_('Active hint')
		else
			_('Inactive hint')
	end
		|| ' #' || c_sh.fk_hint || ' ' || _('suppressed by') || ' ' || c_sh.suppressed_by || E'\n'
		|| coalesce(_('Title: ') || r_vah.title || E'\n', '')
		|| coalesce(_('URL: ') || r_vah.url || E'\n', '')
		|| coalesce(_('Source: ') || r_vah.source || E'\n', '')
		|| coalesce(_('Rationale: ') || c_sh.rationale || E'\n', '')
		|| case when c_sh.md5_sum <> r_vah.md5_sum
			then _('Hint definition has been modified since suppression. Rationale for suppression may no longer apply.') || E'\n'
			else ''
		end
		|| coalesce(_('Hint: ') || r_vah.hint || E'\n', '')
		|| coalesce(_('Recommendation: ') || r_vah.recommendation, '')
		as narrative,
	c_sh.fk_encounter
		as fk_encounter,
	NULL::integer
		as pk_episode,
	NULL::integer
		as pk_health_issue,
	c_sh.pk
		as src_pk,
	'clin.suppressed_hint'::text
		as src_table,
	c_sh.row_version
		as row_version,

	-- issue
	null::text
		as health_issue,
	null::text
		as issue_laterality,
	null::boolean
		as issue_active,
	null::boolean
		as issue_clinically_relevant,
	null::boolean
		as issue_confidential,

	-- episode
	null::text
		as episode,
	null::boolean
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
	clin.suppressed_hint c_sh
		inner join clin.encounter c_enc on (c_sh.fk_encounter = c_enc.pk)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
		inner join ref.v_auto_hints r_vah on (c_sh.fk_hint = r_vah.pk_auto_hint)
;


revoke all on clin.v_suppressed_hints_journal from public;
grant select on clin.v_suppressed_hints_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_suppressed_hints_journal.sql', '22.0');
