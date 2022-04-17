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
comment on table clin.intake is 'List of consumables a patient is/was taking.';

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
comment on column clin.intake.fk_encounter is
	'The episode under which this intake was documented.';

-- --------------------------------------------------------------
-- .narrative
comment on column clin.intake.narrative is
	'Technical/professional notes on this intake, relevant for, say, other providers as opposed to for the patient.';

-- --------------------------------------------------------------
-- .soap_cat

-- --------------------------------------------------------------
-- .use_type
comment on column clin.intake.use_type is
	'
<NULL>: medication, intended use,
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
