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
-- check that .fk_episode of clin.intake and clin.intake_regimen
-- are the same if not discontinued
-- --------------------------------------------------------------
drop function if exists clin.trf_INS_UPD_regimen__check_intake_episode() cascade;

create function clin.trf_INS_UPD_regimen__check_intake_episode()
	returns trigger
	language plpgsql
	as '
DECLARE
	_pk_epi_from_intake integer;
	_pk_epi_from_regimen integer;
BEGIN
	SELECT fk_episode INTO _pk_epi_from_intake
	FROM clin.intake
	WHERE pk = NEW.fk_intake;

	SELECT fk_episode INTO _pk_epi_from_regimen
	FROM clin.intake_regimen
	WHERE pk = NEW.pk;

	IF _pk_epi_from_intake = _pk_epi_from_regimen THEN
		RETURN NULL;
	END IF;

	RAISE EXCEPTION
		''[%] % on %.%: Episode mismatch in active regimen. intake % - episode % / regimen % - episode %'',
			TG_NAME,
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.fk_intake,
			_pk_epi_from_intake,
			NEW.pk,
			_pk_epi_from_regimen
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';

comment on function clin.trf_INS_UPD_regimen__check_intake_episode() is
	'Verifies on INSERT/UPDATE that both the intake_regimen and the
	 intake point to the same episode IF the the regimen is active
	 (IOW, is not historical and .discontinued is not null).';

create constraint trigger tr_INS_UPD_regimen__check_intake_episode
	after insert or update
	on clin.intake_regimen
	deferrable initially deferred
	for each row
		when (NEW.discontinued IS NULL)
		execute procedure clin.trf_INS_UPD_regimen__check_intake_episode();

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-check_intake_vs_regimen.sql', '23.0');
