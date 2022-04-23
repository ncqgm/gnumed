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
-- intakes w/o regimen
drop view if exists clin.v_intakes_w_o_regimen_journal cascade;

create view clin.v_intakes_w_o_regimen_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_i.modified_when,
	c_i.clin_when,
	c_i.modified_by,
	c_i.soap_cat,
	_('intake') || ': '
		|| r_s.description
		|| coalesce(' [' || r_s.atc || ']', '')
		|| (case
			when c_i.use_type = 0 then ' - ' || _('not (harmfully) used')
			when c_i.use_type = 1 then ' - ' || _('presently harmful use')
			when c_i.use_type = 2 then ' - ' || _('presently addicted')
			when c_i.use_type = 3 then ' - ' || _('previously addicted')
			else ''
		end)::text
		|| coalesce(E'\n' || _('intake instructions') || ': ' || r_s.intake_instructions, '')
		|| coalesce(E'\n' || _('patient notes') || ': ' || c_i.notes4patient, '')
		|| coalesce(E'\n' || _('provider notes') || ': ' || c_i.narrative, '')
	|| E'\n' || _('started: unknown')
	|| E'\n' || _('discontinued: unknown')
		as narrative,
	c_i.fk_encounter
		as pk_encounter,
	c_i.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_i.pk
		as src_pk,
	'clin.intake'::text
		as src_table,
	c_i.row_version,
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
	c_epi.description
		as episode,
	c_epi.is_open
		as episode_open,
	c_enc.started
		as encounter_started,
	c_enc.last_affirmed,
	c_ety.description
		as encounter_type,
	_(c_ety.description)
		as encounter_l10n_type
from
	clin.intake c_i
		inner join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
		inner join clin.episode c_epi on c_i.fk_episode = c_epi.pk
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
		inner join ref.substance r_s on (c_i.fk_substance = r_s.pk)
where
	not exists (
		select 1 from clin.intake_regimen c_ir where c_ir.fk_intake = c_i.pk
	)
;

comment on view clin.v_intakes_w_o_regimen_journal is
	'Substance intakes which do not have any associated regimen entries.';

grant select on clin.v_intakes_w_o_regimen_journal to group "gm-doctors";

-- --------------------------------------------------------------
-- start of intake regimen
drop view if exists clin.v_intake_regimen_journal cascade;

create view clin.v_intake_regimen_journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_ir.modified_when,
	case
		when c_ir.comment_on_start = '?' then null
		else c_ir.clin_when
	end::timestamp with time zone
		as started,
	c_ir.modified_by,
	c_ir.soap_cat,
	-- --- narrative ---
	-- line: "start of intake (patient memory)"
	_('start of intake') || coalesce(' (' || c_ir.comment_on_start || ')', '') || E'\n'
	-- line: " planned for 6 months"
	|| coalesce(' ' || _('planned for') || ' ' || c_ir.planned_duration || E'\n', '')
	-- line: " discontinued 1999-03-03 (developed a rash)"
	|| coalesce (
		' ' || _('discontinued') || ' ' || c_ir.discontinued
		|| coalesce(' (' || c_ir.discontinue_reason || ')', '')
		|| E'\n',
		''
	)
	-- line: "Metoprolol 100mg/tablet [ATC code] -- MetoHexal comp Tabletten [ATC code] [PZN 123412345]"
	|| r_s.description || ' '
	|| coalesce (r_d.amount || r_d.unit, '')
	|| coalesce('/' || r_d.dose_unit, '')
	|| coalesce(' [' || r_s.atc || ']', '')
	|| (case
		when c_i.use_type = 0 then ' - ' || _('not (harmfully) used')
		when c_i.use_type = 1 then ' - ' || _('presently harmful use')
		when c_i.use_type = 2 then ' - ' || _('presently addicted')
		when c_i.use_type = 3 then ' - ' || _('previously addicted')
		else ''
	end)::text
	|| coalesce(' -- ' || r_dp.description || ' ' || r_dp.preparation, '')
		|| coalesce(' [' || r_dp.atc_code || ']', '')
		|| coalesce(' [' || r_dp.external_code_type || ' ' || r_dp.external_code || ']', '')
	|| E'\n'
	-- line: "0-1-1 every other day"
	|| ' ' || _('schedule') || ': ' || c_ir.narrative
	-- line: "take with water"
	|| coalesce(E'\n ' || _('intake instructions') || ': ' || r_s.intake_instructions, '')
	-- line: "watch heart rate"
	|| coalesce(E'\n ' || _('patient notes') || ': ' || c_i.notes4patient, '')
	-- line: "does not tolerate higher dose"
	|| coalesce(E'\n ' || _('provider notes') || ': ' || c_i.narrative, '')
		as narrative,
	-- --- narrative ---
	c_ir.fk_encounter
		as pk_encounter,
	c_ir.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_ir.pk
		as src_pk,
	'clin.intake_regimen'::text
		as src_table,
	c_ir.row_version,
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
	c_epi.description
		as episode,
	c_epi.is_open
		as episode_open,
	c_enc.started
		as encounter_started,
	c_enc.last_affirmed,
	c_ety.description
		as encounter_type,
	_(c_ety.description)
		as encounter_l10n_type
from
	clin.intake_regimen c_ir
		inner join clin.intake c_i on (c_ir.fk_intake = c_i.pk)
			inner join ref.substance r_s on (c_i.fk_substance = r_s.pk)
		inner join clin.encounter c_enc on (c_ir.fk_encounter = c_enc.pk)
			inner join clin.encounter_type c_ety on (c_enc.fk_type = c_ety.pk)
		inner join clin.episode c_epi on c_ir.fk_episode = c_epi.pk
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
		left join ref.dose r_d on (c_ir.fk_dose = r_d.pk)
		left join ref.drug_product r_dp on (c_ir.fk_drug_product = r_dp.pk)
;

comment on view clin.v_intake_regimen_journal is
	'Substance intake regimen entries.';

grant select on clin.v_intake_regimen_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intake_journal.sql', '23.0');
