-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
-- After UPDATE of clin.intake check that the resulting row
-- either points to the same substance as before OR any *active*
-- (.discontinued = NULL) linked (clin.intake_regimen.fk_intake)
-- row has also been updated accordingly regarding its .fk_dose.
--
-- The clin.intake_regimen.fk_dose/.fk_drug_product equivalence
-- is asserted on that table directly so no need to check here.
-- --------------------------------------------------------------
drop function if exists clin.trf_UPD_intake___check_regimen_dose_subst() cascade;

create function clin.trf_UPD_intake___check_regimen_dose_subst()
	returns trigger
	language plpgsql
	as '
declare
	_pk_regimen integer;
	_substance_from_intake integer;
	_substance_from_regimen_dose integer;
BEGIN
	SELECT pk INTO _pk_regimen FROM clin.intake_regimen c_ir
	WHERE
		c_ir.fk_intake = NEW.pk
			AND
		c_ir.discontinued IS NULL
	;
	IF NOT FOUND THEN --> no regimen found, all is well
		RETURN NEW;
	END IF;

	SELECT fk_substance into _substance_from_intake FROM clin.intake WHERE pk = NEW.pk;
	SELECT fk_substance into _substance_from_regimen_dose FROM ref.dose WHERE
		pk = (SELECT fk_dose FROM clin.intake_regimen WHERE pk = _pk_regimen)
	;
	IF _substance_from_intake = _substance_from_regimen_dose THEN
		RETURN NEW;
	END IF;

	RAISE EXCEPTION
		''[%] % on %.%: Substance mismatch. Intake % substance % / regimen % dose-substance %.'',
			TG_NAME,
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.pk,
			_substance_from_intake,
			_pk_regimen,
			_substance_from_regimen_dose
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';

comment on function clin.trf_UPD_intake___check_regimen_dose_subst() is
	'If clin.intake.fk_substance is being updated then assert that any dependant *active* clin.intake_regimen rows also point to the new substance.';


create constraint trigger tr_UPD_intake___check_regimen_dose_subst
	after update
	on clin.intake
	deferrable initially deferred
	for each row
		when (NEW.fk_substance IS DISTINCT FROM OLD.fk_substance)
		execute procedure clin.trf_UPD_intake___check_regimen_dose_subst();

-- --------------------------------------------------------------
-- Before INSERT/UPDATE into/of clin.intake_regimen check that
-- clin.intake_regimen.fk_dose is either NULL or points to
-- the same substance (.fk_substance) as the corresponding
-- (clin.intake_regimen.fk_intake) row of clin.intake does.
-- --------------------------------------------------------------
drop function if exists clin.trf_INS_UPD_regimen__check_intake_subst() cascade;

create function clin.trf_INS_UPD_regimen__check_intake_subst()
	returns trigger
	language plpgsql
	as '
declare
	_substance_from_intake integer;
	_substance_from_regimen_dose integer;
BEGIN
	SELECT fk_substance into _substance_from_intake FROM clin.intake WHERE pk = NEW.fk_intake;
	SELECT fk_substance into _substance_from_regimen_dose FROM ref.dose WHERE pk = NEW.fk_dose;
	IF _substance_from_intake = _substance_from_regimen_dose THEN
		RETURN NEW;
	END IF;

	RAISE EXCEPTION
		''[clin.trf_INS_UPD_regimen__check_intake_subst]: INSERT/UPDATE into %.%: Sanity check failed. Regimen % dose-substance = %. Intake % substance = %.'',
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.pk,
			_substance_from_regimen_dose,
			NEW.fk_intake,
			_substance_from_intake
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';

comment on function clin.trf_INS_UPD_regimen__check_intake_subst() is
	'If clin.intake_regimen.fk_dose is not NULL then assert that both
		clin.intake_regimen->ref.dose.pk->ref.dose.fk_substance
	 and
		clin.intake_regimen.fk_intake->clin.intake.pk->clin.intake.fk_substance
	 point to the same ref.substance.pk.';


create trigger tr_INS_UPD_regimen__check_intake_subst
	before insert or update
	on clin.intake_regimen
	for each row
		when (NEW.fk_dose IS NOT NULL)
		execute procedure clin.trf_INS_UPD_regimen__check_intake_subst();

-- --------------------------------------------------------------
-- check that fk_encounter/fk_episode of clin.intake and
-- clin.intake_regimen belong to the same patient
-- --------------------------------------------------------------
drop function if exists clin.trf_INS_UPD_regimen__check_intake_pat() cascade;

create function clin.trf_INS_UPD_regimen__check_intake_pat()
	returns trigger
	language plpgsql
	as '
DECLARE
	_pk_pat_from_intake integer;
	_pk_pat_from_regimen integer;
BEGIN
	SELECT fk_patient INTO _pk_pat_from_intake
	FROM clin.encounter c_enc
	WHERE c_enc.pk = (
		SELECT fk_encounter FROM clin.intake WHERE pk = NEW.fk_intake
	);
	SELECT fk_patient INTO _pk_pat_from_regimen
	FROM clin.encounter c_enc
	WHERE c_enc.pk = NEW.fk_encounter;

	IF _pk_pat_from_intake = _pk_pat_from_regimen THEN
		RETURN NULL;
	END IF;

	RAISE EXCEPTION
		''[%] % on %.%: Patient mismatch. intake % - patient % / regimen % - patient %'',
			TG_NAME,
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.fk_intake,
			_pk_pat_from_intake,
			NEW.pk,
			_pk_pat_from_regimen
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';

comment on function clin.trf_INS_UPD_regimen__check_intake_pat() is
	'Verifies that on INSERT/UPDATE the fk_encounter of both
	 clin.intake and clin.intake_regimen belong to one and the
	 same patient. No need to check fk_episode because fk_encounter
	 vs fk_episode is checked on each table elsewhere.';


create constraint trigger tr_INS_UPD_regimen__check_intake_pat
	after insert or update
	on clin.intake_regimen
	deferrable initially deferred
	for each row
	execute procedure clin.trf_INS_UPD_regimen__check_intake_pat();

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-check_intake_vs_regimen.sql', '23.0');
