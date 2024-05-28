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
-- journal entries listing clin.intakes w/o any regimen
-- --------------------------------------------------------------
drop view if exists clin.v_intakes_w_o_regimen__journal cascade;

create view clin.v_intakes_w_o_regimen__journal as
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
		|| coalesce(E'\n' || _('internal notes') || ': ' || c_i.notes4us, '')
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

comment on view clin.v_intakes_w_o_regimen__journal is
	'Substance intakes which do not have any associated regimen entries.';

grant select on clin.v_intakes_w_o_regimen__journal to group "gm-doctors";

-- --------------------------------------------------------------
-- journal entries for regimens with unknown start time
-- --------------------------------------------------------------
drop view if exists clin.v_regimens_w_o_start__journal cascade;

create view clin.v_regimens_w_o_start__journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_ir.modified_when,
	least(c_ir.modified_when, c_ir.discontinued, c_i.modified_when, c_i.clin_when)
		as clin_when,
	c_ir.modified_by,
	c_ir.soap_cat,
	-- --- narrative ---
	-- line: "start of intake (patient memory)"
	_('intake with uncertain start') || coalesce(' (' || c_ir.comment_on_start || ')', '') || E'\n'
	-- line: " planned for 6 months"
	|| coalesce(' ' || _('planned for') || ' ' || c_ir.planned_duration || E'\n', '')
	-- line: " discontinued 1999-03-03 (developed a rash)"
	|| coalesce (
		' ' || _('discontinued') || ' ' || c_ir.discontinued
		|| coalesce(' (' || c_ir.discontinue_reason || ')', '')
		|| E'\n',
		''
	)
	-- line: "Metoprolol 100mg/tablet [ATC code]"
	|| r_s.description || ' '
	|| c_ir.amount || c_ir.unit
	|| coalesce(' [' || r_s.atc || ']', '')
	|| (case
		when c_i.use_type = 0 then ' - ' || _('not (harmfully) used')
		when c_i.use_type = 1 then ' - ' || _('presently harmful use')
		when c_i.use_type = 2 then ' - ' || _('presently addicted')
		when c_i.use_type = 3 then ' - ' || _('previously addicted')
		else ''
	end)::text
	|| E'\n'
	-- line: "0-1-1 every other day"
	|| ' ' || _('schedule') || ': ' || c_ir.narrative
	-- line: "take with water"
	|| coalesce(E'\n ' || _('intake instructions') || ': ' || r_s.intake_instructions, '')
	-- line: "watch heart rate"
	|| coalesce(E'\n ' || _('patient notes') || ': ' || c_i.notes4patient, '')
	-- line: "does not tolerate higher dose"
	|| coalesce(E'\n ' || _('provider notes') || ': ' || c_i.narrative, '')
	-- line: "is sceptical"
	|| coalesce(E'\n ' || _('internal notes') || ': ' || c_i.notes4us, '')
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
where
	c_ir.start_is_unknown IS TRUE
;

comment on view clin.v_regimens_w_o_start__journal is
	'Substance intake regimen entries with unknown start time.';

grant select on clin.v_regimens_w_o_start__journal to group "gm-doctors";

-- --------------------------------------------------------------
-- journal entries for regimens with known start time
-- --------------------------------------------------------------
drop view if exists clin.v_regimens_w_start__journal cascade;

create view clin.v_regimens_w_start__journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_ir.modified_when,
	c_ir.clin_when,
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
	-- line: "Metoprolol 100mg/tablet [ATC code]"
	|| r_s.description || ' '
	|| c_ir.amount || c_ir.unit
	|| coalesce(' [' || r_s.atc || ']', '')
	|| (case
		when c_i.use_type = 0 then ' - ' || _('not (harmfully) used')
		when c_i.use_type = 1 then ' - ' || _('presently harmful use')
		when c_i.use_type = 2 then ' - ' || _('presently addicted')
		when c_i.use_type = 3 then ' - ' || _('previously addicted')
		else ''
	end)::text
	|| E'\n'
	-- line: "0-1-1 every other day"
	|| ' ' || _('schedule') || ': ' || c_ir.narrative
	-- line: "take with water"
	|| coalesce(E'\n ' || _('intake instructions') || ': ' || r_s.intake_instructions, '')
	-- line: "watch heart rate"
	|| coalesce(E'\n ' || _('patient notes') || ': ' || c_i.notes4patient, '')
	-- line: "does not tolerate higher dose"
	|| coalesce(E'\n ' || _('provider notes') || ': ' || c_i.narrative, '')
	-- line: "is sceptical"
	|| coalesce(E'\n ' || _('internal notes') || ': ' || c_i.notes4us, '')
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
where
	c_ir.start_is_unknown IS FALSE
;

comment on view clin.v_regimens_w_start__journal is
	'Substance intake regimen entries with defined start time.';

grant select on clin.v_regimens_w_start__journal to group "gm-doctors";

-- --------------------------------------------------------------
-- journal entries for regimen discontinuations
-- --------------------------------------------------------------
drop view if exists clin.v_regimens_end__journal cascade;

create view clin.v_regimens_end__journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_ir.modified_when,
	c_ir.discontinued
		as clin_when,
	c_ir.modified_by,
	c_ir.soap_cat,
	-- --- narrative ---
	-- line: "stop of intake (developed a rash)"
	_('stop of intake')
		|| coalesce(' (' || c_ir.discontinue_reason || ')', '')
		|| E'\n'
	-- line: " planned for 6 months"
	|| coalesce(' ' || _('planned for') || ' ' || c_ir.planned_duration || E'\n', '')
	-- line: " started 1999-03-03 (patient memory)"
	|| (case
			when c_ir.comment_on_start = '?' then ''
			else _('started') || ' ' || c_ir.clin_when || coalesce(' (' || c_ir.comment_on_start || ')', '') || E'\n'
	end)::text
	-- line: "Metoprolol 100mg/tablet [ATC code]"
	|| r_s.description || ' '
	|| c_ir.amount || c_ir.unit
	|| coalesce(' [' || r_s.atc || ']', '')
	|| (case
		when c_i.use_type = 0 then ' - ' || _('not (harmfully) used')
		when c_i.use_type = 1 then ' - ' || _('presently harmful use')
		when c_i.use_type = 2 then ' - ' || _('presently addicted')
		when c_i.use_type = 3 then ' - ' || _('previously addicted')
		else ''
	end)::text
	|| E'\n'
	-- line: "0-1-1 every other day"
	|| ' ' || _('schedule') || ': ' || c_ir.narrative
	-- line: "take with water"
	|| coalesce(E'\n ' || _('intake instructions') || ': ' || r_s.intake_instructions, '')
	-- line: "watch heart rate"
	|| coalesce(E'\n ' || _('patient notes') || ': ' || c_i.notes4patient, '')
	-- line: "does not tolerate higher dose"
	|| coalesce(E'\n ' || _('provider notes') || ': ' || c_i.narrative, '')
	-- line: "is sceptical"
	|| coalesce(E'\n ' || _('internal notes') || ': ' || c_i.notes4us, '')
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
where
	c_ir.discontinued IS NOT NULL
;

comment on view clin.v_regimens_end__journal is
	'Substance intake regimen entries end times.';

grant select on clin.v_regimens_end__journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intake_journal.sql', '23.0');
