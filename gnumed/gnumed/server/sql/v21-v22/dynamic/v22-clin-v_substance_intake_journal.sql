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
drop view if exists clin.v_substance_intake_journal cascade;

create view clin.v_substance_intake_journal as

	select
		c_enc.fk_patient
			as pk_patient,
		c_si.modified_when
			as modified_when,
		c_si.clin_when
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = c_si.modified_by),
			'<' || c_si.modified_by || '>'
		)
			as modified_by,
		c_si.soap_cat
			as soap_cat,

		(case
			when is_long_term is true then _('long-term') || ' '
			else ''
		 end
		)
			|| _('substance intake') || ' '
			|| (case
					when intake_is_approved_of is true then _('(approved of)')
					when intake_is_approved_of is false then _('(not approved of)')
					else _('(of unknown approval)')
				end)
			|| ' '
			|| (case
					when harmful_use_type IS NULL then ''
					when harmful_use_type = 0 then _('no harmful use')
					when harmful_use_type = 1 then _('harmful use')
					when harmful_use_type = 2 then _('addiction')
					when harmful_use_type = 3 then _('previous addiction')
				end)
			|| E':\n'

			|| ' ' || r_s.description								-- Metoprolol
			|| coalesce(' [' || r_s.atc || '] ', ' ')				-- [ATC]
			|| r_d.amount::text										-- 100
			|| r_d.unit || ' '										-- mg
			|| _(r_dp.preparation)									-- tab
			|| coalesce(' ' || c_si.schedule, '')					-- 1-0-0
			|| ', ' || (case
					when c_si.comment_on_start = '?' then '?'		-- start = unknown
					when c_si.comment_on_start is NULL then to_char(c_si.clin_when, 'YYYY-MM-DD')				-- 2009-03-01
					else '~' || to_char(c_si.clin_when, 'YYYY-MM-DD') || ' (' || c_si.comment_on_start || ')'	-- ~2009-03-01 (comment)
				end)
			|| coalesce(' -> ' || c_si.duration, '')				-- -> 6 months
			|| E'\n'

			|| coalesce (
				' ' || _('Discontinued') || to_char(c_si.discontinued, ': YYYY-MM-DD')
					|| coalesce(' (' || c_si.discontinue_reason || ')', '')
					|| E'\n',
				''
			)

			|| coalesce(E'\n ' || _('Aim') || ': ' || c_si.aim, '')							-- lower RR
			|| coalesce(E'\n ' || _('Notes') || ': ' || c_si.narrative, '')					-- report if unwell
			|| coalesce(E'\n ' || _('Instructions') || ': ' || r_s.intake_instructions, '')	-- take with a glass of water

			|| coalesce (' "' || r_dp.description || '"'													-- "MetoPharm"
				|| coalesce(' [' || r_dp.atc_code || ']', '')												-- [ATC code]
				|| coalesce(' (' || r_dp.external_code_type || ': ' || r_dp.external_code || ')', ''),		-- (external code)
				'')

		as narrative,

		c_si.fk_encounter
			as pk_encounter,
		c_si.fk_episode
			as pk_episode,
		c_hi.pk
			as pk_health_issue,
		c_si.pk
			as src_pk,
		'clin.substance_intake'::text
			as src_table,
		c_si.row_version
			as row_version,

		-- issue
		c_hi.description
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
		c_epi.description
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
		clin.substance_intake c_si
			inner join ref.lnk_dose2drug r_ld2d on (c_si.fk_drug_component = r_ld2d.pk)
				inner join ref.drug_product r_dp on (r_ld2d.fk_drug_product = r_dp.pk)
				inner join ref.dose r_d on (r_ld2d.fk_dose = r_d.pk)
					inner join ref.substance r_s on (r_d.fk_substance = r_s.pk)
			inner join clin.encounter c_enc on (c_si.fk_encounter = c_enc.pk)
				inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
			inner join clin.episode c_epi on (c_si.fk_episode = c_epi.pk)
				left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
;


grant select on clin.v_substance_intake_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_substance_intake_journal.sql', '22.0');
