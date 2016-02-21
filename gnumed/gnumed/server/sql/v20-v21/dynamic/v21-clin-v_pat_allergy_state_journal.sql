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
drop view if exists clin.v_pat_allergy_state_journal cascade;


create view clin.v_pat_allergy_state_journal as

select
	c_enc.fk_patient
		as pk_patient,
	c_ast.modified_when
		as modified_when,
	coalesce(c_ast.last_confirmed, c_ast.modified_when)
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_ast.modified_by),
		'<' || c_ast.modified_by || '>'
	)
		as modified_by,
	'o'::text
		as soap_cat,
	_('Allergy state') || ': '
		|| case
			when c_ast.has_allergy is null then _('unknown, unasked')
			when c_ast.has_allergy = 0 then _('no known allergies')
			when c_ast.has_allergy = 1 then _('does have allergies')
		   end
		|| coalesce (
			' (' || _('last confirmed') || to_char(c_ast.last_confirmed, ' YYYY-MM-DD HH24:MI') || ')',
			''
		) || coalesce (
			E'\n ' || c_ast.comment,
			''
		) as narrative,
	c_ast.fk_encounter
		as pk_encounter,
	null::integer
		as pk_episode,
	null::integer
		as pk_health_issue,
	c_ast.pk
		as src_pk,
	'clin.allergy_state'::text
		as src_table,
	c_ast.row_version,

	-- issue
	NULL::text
		as health_issue,
	NULL::text
		as issue_laterality,
	NULL::boolean
		as issue_active,
	NULL::boolean
		as issue_clinically_relevant,
	NULL::boolean
		as issue_confidential,

	-- episode
	NULL::text
		as episode,
	NULL::boolean
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
	clin.allergy_state c_ast
		inner join clin.encounter c_enc on (c_ast.fk_encounter = c_enc.pk)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
;


grant select on clin.v_pat_allergy_state_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_pat_allergy_state_journal.sql', '21.0');
