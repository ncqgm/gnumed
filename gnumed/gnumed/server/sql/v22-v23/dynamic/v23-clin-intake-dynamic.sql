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
comment on table clin.intake is 'List of consumables a patient is/was taking.

Each consumable is listed once per patient. IOW a row
documents the fact: "This patient _is_ taking this
substance." regardless of schedule.

Say, a patient takes paracetamol (PCM):

	1000mg PCM in the morning
	500mg PCM at noon
	500mg PCM combined with codeine at night (drug ParaComp)

There will be _one_ clin.intake row for PCM and two (or
three) active regimen rows:

- regimen "500mg PCM, 0-0-1 pk_drug=ParaComp"

	plus either

- regimen "PCM, schedule 1000-500-0, pk_dose=NULL"
	or
- regimen "1000mg PCM, schedule 1-0-0, pk_dose=pcm_1000"
- regimen "500mg PCM, schedule 0-1-0, pk_dose=pcm_500"

Each version is medically correct. Which one is used is
up to the clinician.';

select audit.register_table_for_auditing('clin', 'intake');
select gm.register_notifying_table('clin', 'intake');

grant select, insert, update, delete on clin.intake to "gm-doctors";

-- --------------------------------------------------------------
-- .clin_when
comment on column clin.intake.clin_when is
	'When was this intake last checked with the patient.';

-- --------------------------------------------------------------
-- .fk_encounter
comment on column clin.intake.fk_encounter is
	'The encounter under which this intake was documented.';

-- --------------------------------------------------------------
-- .fk_episode
comment on column clin.intake.fk_episode is
	'The episode under which this intake is currently active.';

-- --------------------------------------------------------------
-- .narrative
comment on column clin.intake.narrative is
	'Technical/professional notes on this intake, relevant for, say, other providers as opposed to for the patient.';

-- --------------------------------------------------------------
-- .soap_cat

-- --------------------------------------------------------------
-- .use_type
comment on column clin.intake.use_type is
'<NULL>: medication, intended use,
0: not used or non-harmful use,
1: presently harmful use,
2: presently addicted,
3: previously addicted';

-- --------------------------------------------------------------
-- .fk_substance
comment on column clin.intake.fk_substance is
	'Substance being taken by patient.';

alter table clin.intake
	add foreign key (fk_substance)
		references ref.substance(pk)
		on delete restrict
		on update cascade;

alter table clin.intake
	alter column fk_substance
		set not NULL;

-- --------------------------------------------------------------
-- ._fk_s_i
comment on column clin.intake._fk_s_i is
	'temporary column pointing to clin.substance_intake.pk this clin.intake row came from during conversion, used to associate a clin.intake_regimen';

-- --------------------------------------------------------------
-- .notes4patient
comment on column clin.intake.notes4patient is
	'Comments on this intake (instructions, caveats, treatment goal, etc) intended for the patient, say, via a medication plan.';

-- --------------------------------------------------------------
-- data transfer
-- --------------------------------------------------------------
-- fill in from clin.substance_intake
INSERT INTO clin.intake (
	fk_encounter,
	fk_episode,
	clin_when,
	narrative,
	notes4patient,
	use_type,
	fk_substance,
	_fk_s_i
)
	SELECT
		c_vsi.pk_encounter,
		c_vsi.pk_episode,
		coalesce(c_vsi.started, now()),
		c_vsi.notes,
		c_vsi.aim,
		c_vsi.harmful_use_type,
		c_vsi.pk_substance,
		c_vsi.pk_substance_intake
	FROM
		clin.v_substance_intakes c_vsi
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake-dynamic.sql', '23.0');
