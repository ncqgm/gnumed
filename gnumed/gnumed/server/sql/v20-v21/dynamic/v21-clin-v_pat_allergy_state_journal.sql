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

UNION ALL

	-- add a copy with all potential sort dates set to now()
	-- that way, we can ensure the allergy state bubbles up to the top
	-- in whatever date sorting scheme is selected thereby improving
	-- patient safety,
	-- the "real" times are mentioned in the narrative
	select
		c_enc.fk_patient
			as pk_patient,
		--c_ast.modified_when
		now()
			as modified_when,
		--coalesce(c_ast.last_confirmed, c_ast.modified_when)
		now()
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_ast.modified_by),
			'<' || c_ast.modified_by || '>'
		)
			as modified_by,
		'o'::text
			as soap_cat,
		_('Allergy state') || ' (' || _('copy') || '): '
			|| case
				when c_ast.has_allergy is null then _('unknown, unasked')
				when c_ast.has_allergy = 0 then _('no known allergies')
				when c_ast.has_allergy = 1 then _('does have allergies')
			   end
			|| coalesce (
				E'\n ' || c_ast.comment,
				''
			) || coalesce (
				-- .clin_when
				E'\n ' || _('last confirmed') || to_char(c_ast.last_confirmed, ' YYYY-MM-DD HH24:MI'),
				''
			) || coalesce (
				-- .modified_when
				E'\n ' || _('entry last modified') || to_char(c_ast.modified_when, ' YYYY-MM-DD HH24:MI'),
				''
			) || coalesce (
				-- .encounter_started
				E'\n ' || _('encounter started') || to_char(c_enc.started, ' YYYY-MM-DD HH24:MI'),
				''
			) || coalesce (
				-- .encounter_last_affirmed
				E'\n ' || _('encounter last affirmed') || to_char(c_enc.last_affirmed, ' YYYY-MM-DD HH24:MI'),
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
		--c_enc.started
		now()
			as encounter_started,
		--c_enc.last_affirmed
		now()
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
