-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table clin.intake is 'Ongoing and historical regimens of consumed substances.
.
There can be any number of discontinued (historic)
and ongoing regimen per substance.
.
There may only ever be one singular non-regimen (amount/unit/schedule)
row per-substance-per-patient at any given time. With-regimen rows
can coexist.

A row without a regimen means "yes, this patient does consume
this substance but we lack further information" -- which cannot
co-exist with rows that store a well-defined regimen for this
substance.';

select audit.register_table_for_auditing('clin', 'intake');
select gm.register_notifying_table('clin', 'intake');

grant select, insert, update, delete on clin.intake to "gm-doctors";

-- --------------------------------------------------------------
-- .clin_when -> "started"
comment on column clin.intake.clin_when is
	'When has intake been started OR has been last verified with the patient (see .comment_on_start).';

-- --------------------------------------------------------------
-- .fk_encounter
comment on column clin.intake.fk_encounter is
	'The encounter under which this intake was recorded/started.';

-- --------------------------------------------------------------
-- .fk_episode
comment on column clin.intake.fk_episode is
'The episode pertinent to this intake.
.
The episodes of regimens need not point to the the same
episode as the intake itself because
.
a) historical (discontinued) regimen are not unlikely
   to relate to episodes other than the current one and
.
b) active regimen may well be *intended* for different episodes, say:
.
Amitriptylin 50-0-0 for depression plus
.
Amitriptylin 0-0-5 for insomnia';

-- --------------------------------------------------------------
-- .narrative
comment on column clin.intake.narrative is
	'concatenation of substance / amount / unit / schedule';


drop function if exists clin.trf__clin_intake__set_narrative() cascade;

create function clin.trf__clin_intake__set_narrative()
	returns trigger
	language plpgsql
	as '
DECLARE
	_subst TEXT;
BEGIN
	SELECT description into _subst FROM ref.substance WHERE pk = NEW.fk_substance;
	NEW.narrative :=_subst
		|| coalesce('' '' || NEW.amount, '''')
		|| coalesce(NEW.unit, '''')
		|| coalesce('' ['' || NEW.schedule || '']'', '''')
	;
	RETURN NEW;
END;';

comment on function clin.trf__clin_intake__set_narrative() is
	'sets clin.intake.narrative from other fields';

create trigger tr__clin_intake__set_narrative
	before insert or update on clin.intake
	for each row
	execute procedure clin.trf__clin_intake__set_narrative();

-- --------------------------------------------------------------
-- .soap_cat
alter table clin.intake
	alter column soap_cat
		set not NULL;

alter table clin.intake
	alter column soap_cat
		set default 'p'::text;

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
-- .amount
comment on column clin.intake.amount is
'The amount of substance (active ingredient) to be taken at each point in time in .schedule.
.
Unrelated to form factor, concentration, or dose per form factor of any drug product.
.
Also not related to route of administration.';

-- --------------------------------------------------------------
-- .unit
comment on column clin.intake.unit is
'The unit (mg/ml/mol/...) for .amount.';

-- --------------------------------------------------------------
-- .schedule
comment on column clin.intake.schedule is 
'The schedule, if any, the substance is to be taken by.
.
Can be a snippet from a controlled vocabulary to be
interpreted by the middleware.';

-- --------------------------------------------------------------
-- .use_type
comment on column clin.intake.use_type is
'The type of (ab)use of this substance, per regimen.
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
		use_type = ANY(ARRAY[NULL::INTEGER, 0, 1, 2, 3])
	);

-- --------------------------------------------------------------
-- .start_is_unknown
comment on column clin.intake.start_is_unknown is 'The start date is entirely unknown';

alter table clin.intake
	alter column start_is_unknown
		set NOT NULL;

alter table clin.intake
	alter column start_is_unknown
		set default false;


drop function if exists clin.trf__start_is_unknown_minimizes_started() cascade;

create or replace function clin.trf__start_is_unknown_minimizes_started()
	returns trigger
	language plpgsql
	as '
BEGIN
	NEW.clin_when := ''-infinity''::timestamp with time zone;
	RETURN NEW;
END;';

create trigger tr__start_is_unknown_minimizes_started
	before insert or update on clin.intake
	for each row
	when (NEW.start_is_unknown is TRUE)
	execute procedure clin.trf__start_is_unknown_minimizes_started()
;

comment on function clin.trf__start_is_unknown_minimizes_started() is
	'When .start_is_unknown is true then .clin_when (used as .started) is set to -infinity.';

-- --------------------------------------------------------------
-- .comment_on_start
comment on column clin.intake.comment_on_start is 'Comment (say, uncertainty level) on .clin_when.';

alter table clin.intake
	alter column comment_on_start
		set default NULL;

-- --------------------------------------------------------------
-- .discontinued
comment on column clin.intake.discontinued is 'When is this intake discontinued ?';

alter table clin.intake
	drop constraint if exists clin_intake__sane_discontinued;

alter table clin.intake
	add constraint clin_intake__sane_discontinued check (
		(discontinued is NULL)
			or
		(discontinued >= clin_when)
	);

-- --------------------------------------------------------------
-- .discontinue_reason
comment on column clin.intake.discontinue_reason is 'Why was this intake discontinued ?';

-- --------------------------------------------------------------
-- .planned_duration
comment on column clin.intake.planned_duration is 'How long is this substance intended to be taken ?';

-- --------------------------------------------------------------
-- .notes4patient
comment on column clin.intake.notes4patient is
'Comments on this intake, eg:
.
- instructions for use ("right after getting up")
- caveats ("report mucosal rashes immediately")
- conditions ("only if systolic RR > 120")
- treatment goal/aim ("heart failure", "lower CVI risk via blood pressure")
- treatment target ("hyperthyroid suppression")
.
intended for the patient, say, on a medication plan.';

-- --------------------------------------------------------------
-- .notes4us
comment on column clin.intake.notes4us is
'Comments on this intake intended for ourselves, eg:
.
- why patient chose this option over a medically preferrable one';

-- --------------------------------------------------------------
-- .notes4providers
comment on column clin.intake.notes4providers is
'Comments on this intake relevant to other providers, eg:
.
- reasoning for unusual dosage/timing';

-- --------------------------------------------------------------
-- .notes4pharmacies
comment on column clin.intake.notes4pharmacies is
'Comments on this intake relevant to dispensing at a pharmacy, say:
.
- "small" pills only
- needs to be divisable';

-- --------------------------------------------------------------
-- table level

-- regimen must be all or nothing
alter table clin.intake drop constraint if exists chk__sane_regimen_if_any cascade;
alter table clin.intake
	add constraint chk__sane_regimen_if_any check (
		(
			(amount IS NULL) AND (unit IS NULL) AND (schedule IS NULL)
		) OR (
			(amount IS DISTINCT FROM NULL) AND (unit IS DISTINCT FROM NULL) AND (schedule IS DISTINCT FROM NULL)
		)
	);


-- if substance4patient has any regimen all rows of the substance for that patient must be regimen
drop function if exists clin.trf__clin_intake__ensure_cross_regimen_integrity() cascade;

create function clin.trf__clin_intake__ensure_cross_regimen_integrity()
	returns trigger
	language plpgsql
	volatile	-- such that INSERT/UPDATE changes will be seen from inside the trigger function
	as '
DECLARE
	__pk_patient integer;
	__row_count integer;
BEGIN
	SELECT clin.map_enc_or_epi_to_patient(NEW.fk_encounter, NEW.fk_episode) INTO __pk_patient;
	PERFORM 1 FROM clin.intake WHERE
		fk_substance = NEW.fk_substance
			AND
		clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode) = __pk_patient
	LIMIT 2;
	GET DIAGNOSTICS __row_count := ROW_COUNT;
	-- a singular row cannot be wrong (can be either with or without regimen fields)
	-- (is it also our very own NEW row btw)
	IF __row_count = 1 THEN
		RETURN NEW;

	END IF;
	-- at this point we have got more than one row,
	-- one of them is our NEW row,
	-- check whether any of them is a non-regimen row
	-- (it does not matter which, existing or NEW)
	PERFORM 1 FROM clin.intake WHERE
		fk_substance = NEW.fk_substance
			AND
		-- checking just .amount is fine because the sane-regimen
		-- check constraint ran before this trigger
		amount IS NULL
			AND
		clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode) = __pk_patient
	LIMIT 1;
	GET DIAGNOSTICS __row_count := ROW_COUNT;
	-- did not find any non-regimen intake,
	-- so having more than one intake is fine
	IF __row_count = 0 THEN
		RETURN NEW;

	END IF;
	-- we now have:
	-- - more than one intake
	-- - at least one of them is non-regimen
	-- which must not happen, non-regimen rows must be
	-- singular per patient+substance
	RAISE EXCEPTION
		''[clin.trf__clin_intake__ensure_cross_regimen_integrity] % on %.% (patient:% / substance:%): Intake rows must either all be with-regimen or a singular non-regimen one, per patient and substance.'',
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			__pk_patient,
			NEW.fk_substance
		USING ERRCODE = ''integrity_constraint_violation''
	;
	RETURN NULL;
END;';

comment on function clin.trf__clin_intake__ensure_cross_regimen_integrity() is
	'Ensure, per substance+patient, that there is either a single non-regimen row OR with-regimen row(s) ONLY';

create constraint trigger tr__clin_intake__ensure_cross_regimen_integrity
	after insert or update on clin.intake
	deferrable initially deferred
	for each row
	execute procedure clin.trf__clin_intake__ensure_cross_regimen_integrity();


-- the combination of (substance, patient, regimen) must be unique
drop index if exists clin.idx__clin_intake__uniq_regimen cascade;
create index idx__clin_intake__uniq_regimen on clin.intake(fk_substance, amount, unit, schedule, clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode));

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake-dynamic.sql', '23.0');
