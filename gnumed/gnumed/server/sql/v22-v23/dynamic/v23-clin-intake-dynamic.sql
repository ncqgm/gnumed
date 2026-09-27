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
		(start_is_unknown IS TRUE)
	or (
		(discontinued is NULL)
			or
		(discontinued >= clin_when)
	)
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
-- --------------------------------------------------------------
drop function if exists clin.trf__adjust_incoming_intake_row() cascade;

create or replace function clin.trf__adjust_incoming_intake_row()
	returns trigger
	language plpgsql
	as '
DECLARE
	_subst TEXT;
BEGIN
	-- on medications:
	IF NEW.use_type IS NULL THEN
		-- set .clin_when (-> started) to minimum if start is unknown
		IF NEW.start_is_unknown is TRUE THEN
			NEW.clin_when := ''-infinity''::timestamp with time zone;
		END IF;
	-- on misuse entries:
	ELSE
		-- force .start_is_unknown to TRUE
		NEW.start_is_unknown := TRUE;
	END IF;
	SELECT description into _subst FROM ref.substance WHERE pk = NEW.fk_substance;
	NEW.narrative :=_subst
		|| coalesce('' '' || NEW.amount, '''')
		|| coalesce(NEW.unit, '''')
		|| coalesce('' ['' || NEW.schedule || '']'', '''')
	;
	RETURN NEW;
END;';

create trigger tr__adjust_incoming_intake_row
	before insert or update on clin.intake
	for each row
	execute procedure clin.trf__adjust_incoming_intake_row()
;

comment on function clin.trf__adjust_incoming_intake_row() is
'Adjust incoming (INSERT/UPDATE) row data:
.
- on medications set start date to -infinity if start is unknown
- on misuse entries force start_is_unknown to True
- set narrative to computed description
';

-- --------------------------------------------------------------
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

-- --------------------------------------------------------------
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
	-- is there an ongoing non-regimen intake ?
	PERFORM 1 FROM clin.intake WHERE
		fk_substance = NEW.fk_substance
			AND
		amount IS NULL
			AND
		((discontinued IS NULL) OR (discontinued > current_timestamp))		-- at start_of_transaction
			AND
		clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode) = __pk_patient
	LIMIT 1;
	GET DIAGNOSTICS __row_count := ROW_COUNT;
	-- no ongoing non-regimen intake ?
	IF __row_count = 0 THEN
		-- then any combination is fine
		RETURN NEW;

	END IF;
	-- at this point we do have an ongoing non-regimen intake,
	-- is there any other ongoing intake, regimen or not ?
	PERFORM 1 FROM clin.intake WHERE
		fk_substance = NEW.fk_substance
			AND
		((discontinued IS NULL) OR (discontinued > current_timestamp))		-- at start_of_transaction
			AND
		clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode) = __pk_patient
	LIMIT 2;
	GET DIAGNOSTICS __row_count := ROW_COUNT;
	-- just one intake ?
	IF __row_count = 1 THEN
		-- that is fine (must be the ongoing non-regimen one btw)
		RETURN NEW;

	END IF;
	-- at this point there is more than one ongoing intake
	-- and one of them is non-regimen
	-- which is not allowed: ongoing non-regimen rows
	-- must be singular per patient+substance
	RAISE EXCEPTION
		''[clin.trf__clin_intake__ensure_cross_regimen_integrity] % on %.% (patient:% / substance:%): An _ongoing_ non-regimen intake cannot coexist with any other ongoing intake for this patient and substance.'',
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
	'Ensure, per substance+patient, that any ongoing non-regimen row is singular.
.
Considerata:
.
Kirk took ibuprofen for a treatment regimen, back in september 2018. This is registered in GNUmed
as an old, discontinued intake, with a set treatment regimen (amount, unit, schedule).
.
Today, Kirk tells Dr. McCoy that he is taking ibuprofen fairly regularly due to tooth aches (?),
but he does not remember dosages or really how often he takes it
.
.
If I add a morphine intake to a patient, say Kirk, with or without a treatment regimen,
and then hypothetically Kirk becomes dependent/addicted to it and so I try to add that
as a substance abuse via EMR -> Manage -> Substance abuse, I am not able to do so. That
happens even if I discontinue that morphine intake saved via the medication plugin.
';

create constraint trigger tr__clin_intake__ensure_cross_regimen_integrity
	after insert or update on clin.intake
	deferrable initially deferred
	for each row
	execute procedure clin.trf__clin_intake__ensure_cross_regimen_integrity();

-- --------------------------------------------------------------
-- the combination of (substance, patient, regimen) must be unique
drop index if exists clin.idx__clin_intake__uniq_regimen cascade;
create unique index idx__clin_intake__uniq_regimen
	on clin.intake (
		fk_substance,
		amount,
		unit,
		schedule,
		discontinued,
		clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode)
	)
	NULLS not distinct
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake-dynamic.sql', '23.0');
