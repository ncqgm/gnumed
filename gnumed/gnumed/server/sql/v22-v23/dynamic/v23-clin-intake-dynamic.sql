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
substance." regardless of schedule.';

select audit.register_table_for_auditing('clin', 'intake');
select gm.register_notifying_table('clin', 'intake');

grant select, insert, update, delete on clin.intake to "gm-doctors";

-- --------------------------------------------------------------
-- .clin_when
comment on column clin.intake.clin_when is
'When this intake was last verified with the patient.
.
Will mostly amount to when intake of this substance was initially recorded at all.';

-- --------------------------------------------------------------
-- .fk_encounter
comment on column clin.intake.fk_encounter is
	'The encounter under which this intake was recorded.';

-- --------------------------------------------------------------
-- .fk_episode
comment on column clin.intake.fk_episode is
	'The episode pertinent to this intake as long as there is no intake regimen.';

-- --------------------------------------------------------------
-- .narrative
comment on column clin.intake.narrative is
	'reason / aim / what for ? / why ?  for intake of this substance';
--	'Technical/professional notes on this intake, relevant for, say, other providers as opposed to for the patient.';

-- --------------------------------------------------------------
-- .soap_cat

-- --------------------------------------------------------------
-- .use_type
comment on column clin.intake.use_type is
'Only valid if no clin.intake_regimen rows exist for this intakt.
.
invalid:
-1: clin.intake_regimen rows exist
.
"normal" substances:
 <NULL>: medication, intended use
addictives:
 0: not used or non-harmful use,
 1: presently harmful use,
 2: presently addicted,
 3: previously addicted
.
Per-regimen because possible co-existence of eg:
 "CBD drops 15-0-0" -- controlled use in, say, multiple sclerosis or chronic pain
 	-> .use_type = <NULL>
.
 	_and_
.
 "marihuana smoke" -- lifestyle/uncontrolled/non-medical use
 	-> .use_type = 0-3
';

alter table clin.intake
	drop constraint if exists chk__sane_use_type cascade;

alter table clin.intake
	add constraint chk__sane_use_type check (
		use_type = ANY(ARRAY[-1, NULL::INTEGER, 0, 1, 2, 3])
	);

drop function if exists clin.trf__clin__intake__unset_use_type() cascade;

create function clin.trf__clin__intake__unset_use_type()
	returns trigger
	language plpgsql
	as '
BEGIN
	PERFORM 1 FROM clin.intake_regimen WHERE fk_intake = NEW.pk LIMIT 1;
	IF FOUND THEN
		RETURN NEW;
	END IF;
	NEW.use_type := -1;
	RETURN NEW;
END;';

comment on function clin.trf__clin__intake__unset_use_type() is
	'When UPDATEing a clin.intake unset .use_type if any linked clin.intake_regimen rows exist';

create trigger tr__unset_use_type
	before update on clin.intake
	for each row
	when (NEW.use_type <> -1)
	execute procedure clin.trf__clin__intake__unset_use_type();

-- --------------------------------------------------------------
-- .fk_substance
comment on column clin.intake.fk_substance is
'Substance being taken by patient.
.
Must be unique per patient.';

alter table clin.intake
	add foreign key (fk_substance)
		references ref.substance(pk)
		on delete restrict
		on update cascade;

alter table clin.intake
	alter column fk_substance
		set not NULL;

drop index if exists clin.idx_uniq_substance_per_patient cascade;
create unique index idx_uniq_substance_per_patient on clin.intake(fk_substance, clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode));

-- --------------------------------------------------------------
-- ._fk_s_i
comment on column clin.intake._fk_s_i is
	'temporary column pointing to the clin.substance_intake.pk this clin.intake row came from during conversion, used for associating a clin.intake_regimen';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake-dynamic.sql', '23.0');
