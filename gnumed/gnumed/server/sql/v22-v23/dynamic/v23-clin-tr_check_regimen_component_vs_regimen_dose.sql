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
drop function if exists clin.trf_check_regimen_component_vs_regimen_dose() cascade;


create function clin.trf_check_regimen_component_vs_regimen_dose()
	returns trigger
	language plpgsql
	as '
DECLARE
	_pk_dose_from_component integer;
BEGIN
	SELECT fk_dose INTO _pk_dose_from_component FROM ref.lnk_dose2drug WHERE pk = NEW.fk_drug_component;
	IF _pk_dose_from_component = NEW.fk_dose THEN
		RETURN NEW;
	END IF;

	RAISE EXCEPTION
		''[clin.trf_check_regimen_component_vs_regimen_dose]: INSERT/UPDATE into %.%: Sanity check failed. clin.intake_regimen.pk=%, clin.intake_regimen.fk_dose=%, clin.intake_regimen.fk_drug_component=ref.lnk_dose2drug.pk=% -> ref.lnk_dose2drug.fk_dose=%'',
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.pk,
			NEW.fk_dose,
			NEW.fk_drug_component,
			_substance_from_regimen_dose
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';


comment on function clin.trf_check_regimen_component_vs_regimen_dose() is
	'If clin.intake_regimen.fk_dose is not NULL then assert that both
		clin.intake_regimen->ref.dose.pk->ref.dose.fk_substance
	 and
		clin.intake_regimen.fk_intake->clin.intake.pk->clin.intake.fk_substance
	 point to the same ref.substance.pk.';


create trigger tr_check_regimen_component_vs_regimen_dose
	before insert or update
	on clin.intake_regimen
	for each row
		when ((NEW.fk_drug_component IS NOT NULL) and (NEW.fk_dose IS NOT NULL))
		execute procedure clin.trf_check_regimen_component_vs_regimen_dose();


-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-tr_check_regimen_component_vs_regimen_dose.sql', '23.0');
