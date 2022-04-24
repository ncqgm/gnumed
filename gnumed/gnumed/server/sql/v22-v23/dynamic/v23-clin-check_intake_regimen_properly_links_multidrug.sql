-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
drop function if exists clin.verify__multidrug_not_linked2patient(_pk_patient integer, _pk_drug integer) cascade;

create function clin.verify__multidrug_not_linked2patient(_pk_patient integer, _pk_drug integer)
	returns boolean
	language plpgsql
	as '
DECLARE
	_component_count_in_drug integer;
	_multidrug_is_linked boolean;
BEGIN
	SELECT COUNT(1) INTO _component_count_in_drug
	FROM ref.lnk_dose2drug r_ld2d
	WHERE r_ld2d.fk_drug_product = _pk_drug;

	-- multi-drug at all ?
	IF _component_count_in_drug < 2 THEN
		-- no further checks needed
		RETURN TRUE;
	END IF;

	SELECT EXISTS (
		SELECT 1 FROM clin.intake_regimen c_ir
		WHERE
			c_ir.discontinued IS NULL
				AND
			c_ir.fk_drug_product = _pk_drug
				AND
			c_ir.fk_intake IN (
				SELECT pk FROM clin.intake c_i
				WHERE
					c_i.fk_encounter IN (SELECT pk FROM clin.encounter WHERE fk_patient = _pk_patient)
			)
	) into _multidrug_is_linked;
	RETURN _multidrug_is_linked IS FALSE;
END;';

comment on function clin.verify__multidrug_not_linked2patient(_pk_patient integer, _pk_drug integer) is
	'Checks whether a multi-component drug is taken by a patient or not.
	 Arguments: patient PK, drug PK;
	 Returns:
	  TRUE: not a multi-drug or not taken by patient,
	  FALSE: patient takes this drug';

-- grant to clinical staff

-- --------------------------------------------------------------
drop function if exists clin.verify__all_multidrug_components_linked2patient(_pk_patient integer, _pk_drug integer) cascade;

create function clin.verify__all_multidrug_components_linked2patient(_pk_patient integer, _pk_drug integer)
	returns boolean
	language plpgsql
	as '
DECLARE
	_component_count_in_drug integer;
	_component_count_linked integer;
BEGIN
	SELECT COUNT(1) INTO _component_count_in_drug
	FROM ref.lnk_dose2drug r_ld2d
	WHERE r_ld2d.fk_drug_product = _pk_drug;

	-- multi-drug at all ?
	IF _component_count_in_drug < 2 THEN
		-- no further checks needed
		RETURN TRUE;
	END IF;

	SELECT COUNT(1) into _component_count_linked
	FROM clin.intake_regimen c_ir
	WHERE
		c_ir.discontinued IS NULL
			AND
		c_ir.fk_drug_product = _pk_drug
			AND
		c_ir.fk_intake IN (
			SELECT pk FROM clin.intake c_i
			WHERE
				c_i.fk_encounter IN (SELECT pk FROM clin.encounter WHERE fk_patient = _pk_patient)
		)
	;
	RETURN _component_count_linked = _component_count_in_drug;
END;';

comment on function clin.verify__all_multidrug_components_linked2patient(_pk_patient integer, _pk_drug integer) is
	'Verifies that all components of a multi-component drug are linked
	 to a patient, if at all.
	 Arguments: patient PK, drug PK;
	 Returns:
	  TRUE: all linked
	  FALSE: not all linked';

-- grant to clinical staff

-- --------------------------------------------------------------
-- after DELETE of multidrug intake regimen *all*
-- components must have been removed from the patient
-- --------------------------------------------------------------
drop function if exists clin.trf_check_intake_regimen_on_del_multidrug() cascade;

create function clin.trf_check_intake_regimen_on_del_multidrug()
	returns trigger
	language plpgsql
	as '
DECLARE
	_pk_patient integer;
BEGIN
	SELECT clin.map_enc_or_epi_to_patient(OLD.fk_encounter, OLD.fk_episode) INTO _pk_patient;

	IF clin.verify__multidrug_not_linked2patient(_pk_patient, OLD.fk_drug_product) IS TRUE THEN
		RETURN NULL;
	END IF;

	RAISE EXCEPTION
		''[%] - % on %.%: All components of multi-drug must be unlinked together. clin.intake_regimen.pk=% / clin.intake_regimen.fk_intake=% / clin.intake_regimen.fk_drug_product=% / pk_patient=%'',
			TG_NAME,
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			OLD.pk,
			OLD.fk_intake,
			OLD.fk_drug_product,
			_pk_patient
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';


comment on function clin.trf_check_intake_regimen_on_del_multidrug() is
	'Checks that when deleting an intake regimen all components of a multi-component drug have been removed from the patient at the end of that transaction.';

create constraint trigger tr_check_intake_regimen_on_del_multidrug
	after delete
	on clin.intake_regimen
	deferrable initially deferred
	for each row
	-- anything to check ?
	when (OLD.fk_drug_product IS NOT NULL)
	execute procedure clin.trf_check_intake_regimen_on_del_multidrug();

-- --------------------------------------------------------------
-- after INSERT of a multidrug intake regimen *all*
-- components must be linked to that patient
-- --------------------------------------------------------------
drop function if exists clin.trf_check_intake_regimen_on_ins_multidrug() cascade;

create function clin.trf_check_intake_regimen_on_ins_multidrug()
	returns trigger
	language plpgsql
	as '
DECLARE
	_pk_patient integer;
BEGIN
	SELECT clin.map_enc_or_epi_to_patient(NEW.fk_encounter, NEW.fk_episode) INTO _pk_patient;

	IF clin.verify__all_multidrug_components_linked2patient(_pk_patient, NEW.fk_drug_product) IS TRUE THEN
		RETURN NULL;
	END IF;

	RAISE EXCEPTION
		''[%] - % on %.%: All components of multi-drug must be inserted together. clin.intake_regimen.pk=% / clin.intake_regimen.fk_intake=% / clin.intake_regimen.fk_drug_product=% / pk_patient=%'',
			TG_NAME,
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.pk,
			NEW.fk_intake,
			NEW.fk_drug_product,
			_pk_patient
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';


comment on function clin.trf_check_intake_regimen_on_ins_multidrug() is
	'Checks that when inserting an intake regimen all components of a multi-component drug have been added to the patient at the end of that transaction.';

create constraint trigger tr_check_intake_regimen_on_ins_multidrug
	after insert
	on clin.intake_regimen
	deferrable initially deferred
	for each row
	-- anything to check ?
	when (NEW.fk_drug_product IS NOT NULL)
	execute procedure clin.trf_check_intake_regimen_on_ins_multidrug();

-- --------------------------------------------------------------
-- after UPDATE of a multidrug intake regimen *all*
-- NEW components must be linked to that patient
-- and OLD components must have been removed from the
-- patient
-- --------------------------------------------------------------
drop function if exists clin.trf_check_intake_regimen_on_upd_multidrug() cascade;

create function clin.trf_check_intake_regimen_on_upd_multidrug()
	returns trigger
	language plpgsql
	as '
DECLARE
	_pk_patient integer;
BEGIN
	-- .fk_drug_product: NULL -> NULL: does not occur (trigger condition)
	-- .fk_drug_product: OLD = NEW: does not happen (trigger condition)

	SELECT clin.map_enc_or_epi_to_patient(OLD.fk_encounter, OLD.fk_episode) into _pk_patient;

	-- .fk_drug_product: OLD -> NULL: behaves like DELETE
	IF NEW.fk_drug_product IS NULL THEN
		IF clin.verify__multidrug_not_linked2patient(_pk_patient, OLD.fk_drug_product) IS TRUE THEN
			RETURN NULL;
		END IF;
		RAISE EXCEPTION
			''[%] - % on %.%: All components of multi-drug must be unlinked together. clin.intake_regimen.pk=% / clin.intake_regimen.fk_intake=% / clin.intake_regimen.fk_drug_product=% / pk_patient=%'',
				TG_NAME,
				TG_OP,
				TG_TABLE_SCHEMA,
				TG_TABLE_NAME,
				OLD.pk,
				OLD.fk_intake,
				OLD.fk_drug_product,
				_pk_patient
			USING ERRCODE = ''assert_failure''
		;
	END IF;

	-- .fk_drug_product: NULL -> NEW: behaves like INSERT
	IF OLD.fk_drug_product IS NULL THEN
		IF clin.verify__all_multidrug_components_linked2patient(_pk_patient, NEW.fk_drug_product) IS TRUE THEN
			RETURN NULL;
		END IF;
		RAISE EXCEPTION
			''[%] - % on %.%: All components of multi-drug must be inserted together. clin.intake_regimen.pk=% / clin.intake_regimen.fk_intake=% / clin.intake_regimen.fk_drug_product=% / pk_patient=%'',
				TG_NAME,
				TG_OP,
				TG_TABLE_SCHEMA,
				TG_TABLE_NAME,
				NEW.pk,
				NEW.fk_intake,
				NEW.fk_drug_product,
				_pk_patient
			USING ERRCODE = ''assert_failure''
		;
	END IF;

	-- .fk_drug_product: OLD -> NEW: true UPDATE
	-- 1) assert DEL of OLD
	IF clin.verify__multidrug_not_linked2patient(_pk_patient, OLD.fk_drug_product) IS TRUE THEN
		RETURN NULL;
	END IF;
	RAISE EXCEPTION
		''[%] - % on %.%: All components of previous multi-drug must be unlinked together. clin.intake_regimen.pk=% / clin.intake_regimen.fk_intake=% / clin.intake_regimen.fk_drug_product=% / pk_patient=%'',
			TG_NAME,
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			OLD.pk,
			OLD.fk_intake,
			OLD.fk_drug_product,
			_pk_patient
		USING ERRCODE = ''assert_failure''
	;
	-- 2) assert INS of NEW
	IF clin.verify__all_multidrug_components_linked2patient(_pk_patient, NEW.fk_drug_product) IS TRUE THEN
		RETURN NULL;
	END IF;
	RAISE EXCEPTION
		''[%] - % on %.%: All components of multi-drug must be updated to together. clin.intake_regimen.pk=% / clin.intake_regimen.fk_intake=% / clin.intake_regimen.fk_drug_product=% / pk_patient=%'',
			TG_NAME,
			TG_OP,
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.pk,
			NEW.fk_intake,
			NEW.fk_drug_product,
			_pk_patient
		USING ERRCODE = ''assert_failure''
	;

	RETURN NULL;
END;';


comment on function clin.trf_check_intake_regimen_on_upd_multidrug() is
	'Checks that when updating an intake regimen all components of a multi-component drug have been updated the same way on the patient at the end of that transaction.';

create constraint trigger tr_check_intake_regimen_on_upd_multidrug
	after update
	on clin.intake_regimen
	deferrable initially deferred
	for each row
	-- anything to check ?
	when (NEW.fk_drug_product IS DISTINCT FROM OLD.fk_drug_product)
	execute procedure clin.trf_check_intake_regimen_on_upd_multidrug();

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-check_intake_regimen_properly_links_multidrug.sql', '23.0');
