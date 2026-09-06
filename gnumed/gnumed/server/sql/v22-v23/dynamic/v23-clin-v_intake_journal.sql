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
-- old views
drop view if exists clin.v_intakes_w_o_regimen__journal cascade;
drop view if exists clin.v_regimens_w_start__journal cascade;
drop view if exists clin.v_regimens_w_o_start__journal cascade;
drop view if exists clin.v_regimens_end__journal cascade;

-- --------------------------------------------------------------
-- journal entries for intakes, at start of intake
-- --------------------------------------------------------------
drop view if exists clin.v_intakes_at_start__journal cascade;

create view clin.v_intakes_at_start__journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_i.modified_when,
	c_i.clin_when,
	c_i.modified_by,
	c_i.soap_cat,
	-- --- narrative ---
	-- line 1
	(select _('start of')) || ': ' || c_i.narrative || E'\n'
	-- lines 2+
	-- line: "start of intake (per patient memory)"
	|| coalesce(' ' || c_i.comment_on_start, '') || E'\n'
	-- line: " planned for 6 months"
	|| coalesce(' ' || (select _('planned for')) || ' ' || c_i.planned_duration || E'\n', '')
	-- line: " discontinued 1999-03-03 (developed a rash)"
	|| coalesce (
		' ' || (select _('discontinued')) || ' ' || c_i.discontinued
		|| coalesce(' (' || c_i.discontinue_reason || ')', '')
		|| E'\n',
		''
	)
	|| (case
		when c_i.use_type = 0 then ' - ' || (select _('not (harmfully) used'))
		when c_i.use_type = 1 then ' - ' || (select _('presently harmful use'))
		when c_i.use_type = 2 then ' - ' || (select _('presently addicted'))
		when c_i.use_type = 3 then ' - ' || (select _('previously addicted'))
		else ''
	end)::text
	-- line: "100mg @ 0-1-1 every other day"
	|| coalesce(E'\n ' || (select _('schedule')) || ': ' || c_i.amount || c_i.unit || ' @ ' || c_i.schedule, '')
	-- line: "take with water"
	|| coalesce(E'\n ' || (select _('intake instructions')) || ': ' || r_s.intake_instructions, '')
	-- line: "watch heart rate"
	|| coalesce(E'\n ' || (select _('patient notes')) || ': ' || c_i.notes4patient, '')
	-- line: "does not tolerate higher dose"
	|| coalesce(E'\n ' || (select _('provider notes')) || ': ' || c_i.notes4providers, '')
	-- line: "is sceptical"
	|| coalesce(E'\n ' || (select _('internal notes')) || ': ' || c_i.notes4us, '')
	-- line: "dispense divisible tablets"
	|| coalesce(E'\n ' || (select _('pharmacy notes')) || ': ' || c_i.notes4pharmacies, '')
	|| coalesce(E'\n ' || 'ATC: ' || r_s.atc, '')
		as narrative,
	-- --- narrative ---
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
	c_enc.fk_type
		AS pk_encounter_type
from
	clin.intake c_i
		inner join ref.substance r_s on (c_i.fk_substance = r_s.pk)
	inner join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
	inner join clin.episode c_epi on c_i.fk_episode = c_epi.pk
		left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
where
	c_i.start_is_unknown IS FALSE
;

comment on view clin.v_intakes_at_start__journal is
	'Substance intake entries with defined start time, sorted at start time.';

grant select on clin.v_intakes_at_start__journal to group "gm-doctors";

-- -----------------------------------------------------------------------
-- journal entries for intake discontinuations, at discontinuation time
-- -----------------------------------------------------------------------
drop view if exists clin.v_intakes_at_end__journal cascade;

create view clin.v_intakes_at_end__journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_i.modified_when,
	c_i.discontinued
		as clin_when,
	c_i.modified_by,
	c_i.soap_cat,
	-- --- narrative ---
	-- line 1
	(select _('stopped')) || ': ' || c_i.narrative || coalesce(' (' || c_i.discontinue_reason || ')', '') || E'\n'
	-- lines 2+
	-- line: " started 1999-03-03 (per patient memory)"
	|| (case
			when c_i.comment_on_start = '?' then ''
			else _('started') || ' ' || c_i.clin_when || coalesce(' (' || c_i.comment_on_start || ')', '') || E'\n'
	end)::text
	-- line: " planned for 6 months"
	|| coalesce(' ' || (select _('planned for')) || ' ' || c_i.planned_duration || E'\n', '')
	-- line: " discontinued 1999-03-03 (developed a rash)"
	|| coalesce (
		' ' || (select _('discontinued')) || ' ' || c_i.discontinued
		|| coalesce(' (' || c_i.discontinue_reason || ')', '')
		|| E'\n',
		''
	)
	|| (case
		when c_i.use_type = 0 then ' - ' || (select _('not (harmfully) used'))
		when c_i.use_type = 1 then ' - ' || (select _('presently harmful use'))
		when c_i.use_type = 2 then ' - ' || (select _('presently addicted'))
		when c_i.use_type = 3 then ' - ' || (select _('previously addicted'))
		else ''
	end)::text
	-- line: "100mg @ 0-1-1 every other day"
	|| coalesce(E'\n ' || (select _('schedule')) || ': ' || c_i.amount || c_i.unit || ' @ ' || c_i.schedule, '')
	-- line: "take with water"
	|| coalesce(E'\n ' || (select _('intake instructions')) || ': ' || r_s.intake_instructions, '')
	-- line: "watch heart rate"
	|| coalesce(E'\n ' || (select _('patient notes')) || ': ' || c_i.notes4patient, '')
	-- line: "does not tolerate higher dose"
	|| coalesce(E'\n ' || (select _('provider notes')) || ': ' || c_i.notes4providers, '')
	-- line: "is sceptical"
	|| coalesce(E'\n ' || (select _('internal notes')) || ': ' || c_i.notes4us, '')
	-- line: "dispense divisible tablets"
	|| coalesce(E'\n ' || (select _('pharmacy notes')) || ': ' || c_i.notes4pharmacies, '')
	|| coalesce(E'\n ' || 'ATC: ' || r_s.atc, '')
		as narrative,
	-- --- narrative ---
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
	c_enc.fk_type
		AS pk_encounter_type
from
	clin.intake c_i
		inner join ref.substance r_s on (c_i.fk_substance = r_s.pk)
	inner join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
	inner join clin.episode c_epi on c_i.fk_episode = c_epi.pk
		left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
where
	c_i.discontinued IS NOT NULL
;

comment on view clin.v_intakes_at_end__journal is
	'Substance intake entries with defined discontinue time, sorted at discontinue time.';

grant select on clin.v_intakes_at_end__journal to group "gm-doctors";

-- --------------------------------------------------------------
-- journal entries for intakes with unknown start and end time
-- --------------------------------------------------------------
drop view if exists clin.v_intakes_w_o_start_and_end__journal cascade;

create view clin.v_intakes_w_o_start_and_end__journal as
select
	c_enc.fk_patient
		as pk_patient,
	c_i.modified_when,
	c_i.clin_when,
	c_i.modified_by,
	c_i.soap_cat,
	-- --- narrative ---
	-- line 1
	(select _('intake of')) || ': ' || c_i.narrative || E'\n'
	-- lines 2+
	-- line: "start of intake (per patient memory)"
	|| coalesce(' ' || c_i.comment_on_start, '') || E'\n'
	-- line: " planned for 6 months"
	|| coalesce(' ' || (select _('planned for')) || ' ' || c_i.planned_duration || E'\n', '')
	|| (case
		when c_i.use_type = 0 then ' - ' || (select _('not (harmfully) used'))
		when c_i.use_type = 1 then ' - ' || (select _('presently harmful use'))
		when c_i.use_type = 2 then ' - ' || (select _('presently addicted'))
		when c_i.use_type = 3 then ' - ' || (select _('previously addicted'))
		else ''
	end)::text
	-- line: "100mg @ 0-1-1 every other day"
	|| coalesce(E'\n ' || (select _('schedule')) || ': ' || c_i.amount || c_i.unit || ' @ ' || c_i.schedule, '')
	-- line: "take with water"
	|| coalesce(E'\n ' || (select _('intake instructions')) || ': ' || r_s.intake_instructions, '')
	-- line: "watch heart rate"
	|| coalesce(E'\n ' || (select _('patient notes')) || ': ' || c_i.notes4patient, '')
	-- line: "does not tolerate higher dose"
	|| coalesce(E'\n ' || (select _('provider notes')) || ': ' || c_i.notes4providers, '')
	-- line: "is sceptical"
	|| coalesce(E'\n ' || (select _('internal notes')) || ': ' || c_i.notes4us, '')
	-- line: "dispense divisible tablets"
	|| coalesce(E'\n ' || (select _('pharmacy notes')) || ': ' || c_i.notes4pharmacies, '')
	|| coalesce(E'\n ' || 'ATC: ' || r_s.atc, '')
		as narrative,
	-- --- narrative ---
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
	c_enc.fk_type
		AS pk_encounter_type
from
	clin.intake c_i
		inner join ref.substance r_s on (c_i.fk_substance = r_s.pk)
	inner join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
	inner join clin.episode c_epi on c_i.fk_episode = c_epi.pk
		left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
where
	c_i.start_is_unknown IS TRUE
		AND
	c_i.discontinued IS NULL
;

comment on view clin.v_intakes_w_o_start_and_end__journal is
	'Substance intake entries without start and end time.';

grant select on clin.v_intakes_w_o_start_and_end__journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intake_journal.sql', '23.0');
