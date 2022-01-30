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
-- clin.intake vs clin.intake_regimen
drop function if exists clin.trf_check_subst_on_intake_vs_regimen_dose() cascade;

create function clin.trf_check_subst_on_intake_vs_regimen_dose()
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
		''[clin.trf_check_subst_on_intake_vs_regimen_dose]: INSERT/UPDATE into %.%: Sanity check failed. Regimen % dose-substance = %. Intake % substance = %.'',
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

comment on function clin.trf_check_subst_on_intake_vs_regimen_dose() is
	'If clin.intake_regimen.fk_dose is not NULL then assert that both
		clin.intake_regimen->ref.dose.pk->ref.dose.fk_substance
	 and
		clin.intake_regimen.fk_intake->clin.intake.pk->clin.intake.fk_substance
	 point to the same ref.substance.pk.';


create trigger tr_check_subst_on_intake_vs_regimen_dose
	before insert or update
	on clin.intake_regimen
	for each row
		when (NEW.fk_dose IS NOT NULL)
		execute procedure clin.trf_check_subst_on_intake_vs_regimen_dose();

-- --------------------------------------------------------------
-- check that fk_encounter/fk_episode of clin.intake and
-- clin.intake_regimen belong to the same patient
-- --------------------------------------------------------------
drop function if exists clin.trf_ins_upd_check_pat_on_intake_vs_regimen() cascade;

create function clin.trf_ins_upd_check_pat_on_intake_vs_regimen()
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
	WHERE c_enc.pk = (
		SELECT fk_encounter FROM clin.intake_regimen WHERE pk = NEW.pk
	);

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

comment on function clin.trf_ins_upd_check_pat_on_intake_vs_regimen() is
	'Verifies that on INSERT/UPDATE the fk_encounter and fk_episode of
	 both clin.intake and clin.intake_regimen belong to one and the
	 same patient.';


create constraint trigger tr_ins_upd_check_pat_on_intake_vs_regimen
	after insert or update
	on clin.intake_regimen
	deferrable initially deferred
	for each row
	execute procedure clin.trf_ins_upd_check_pat_on_intake_vs_regimen();

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-check_intake_vs_regimen.sql', '23.0');
