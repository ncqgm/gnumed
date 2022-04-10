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
drop function if exists clin.trf_check_regimen_drug_vs_regimen_dose() cascade;


create function clin.trf_check_regimen_drug_vs_regimen_dose()
	returns trigger
	language plpgsql
	as '
BEGIN
	PERFORM 1 FROM ref.lnk_dose2drug r_ld2d
	WHERE
		r_ld2d.fk_drug_product = NEW.fk_drug_product
			AND
		r_ld2d.fk_dose = NEW.fk_dose
	;
	IF FOUND THEN
		RETURN NEW;
	END IF;

	RAISE EXCEPTION
		''[clin.trf_check_regimen_drug_vs_regimen_dose]: INSERT/UPDATE into %.%: Dose does not belong to drug. clin.intake_regimen.pk=%, clin.intake_regimen.fk_dose=%, clin.intake_regimen.fk_drug_product=ref.lnk_dose2drug.fk_drug_product=%'',
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.pk,
			NEW.fk_dose,
			NEW.fk_drug_product
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';


comment on function clin.trf_check_regimen_drug_vs_regimen_dose() is
	'If clin.intake_regimen.fk_drug_product is not NULL then assert that
	 the dose is linked to the drug in question as a component.';


create trigger tr_check_regimen_drug_vs_regimen_dose
	before insert or update
	on clin.intake_regimen
	for each row
		when (NEW.fk_drug_product IS NOT NULL)
		execute procedure clin.trf_check_regimen_drug_vs_regimen_dose();

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-tr_check_regimen_drug_vs_regimen_dose.sql', '23.0');
