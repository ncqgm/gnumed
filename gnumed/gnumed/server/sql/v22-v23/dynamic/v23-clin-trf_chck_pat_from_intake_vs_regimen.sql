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
drop function if exists clin.trf_chck_pat_from_intake_vs_regimen() cascade;


create or replace function clin.trf_chck_pat_from_intake_vs_regimen()
	returns trigger
	language plpgsql
	as '
declare
	_identity_from_regimen integer;
	_identity_from_intake integer;
begin
	-- no check if no change, can only apply on update
	IF TG_OP = ''UPDATE'' THEN
		IF NEW.fk_encounter = OLD.fk_encounter AND NEW.fk_episode = OLD.fk_episode THEN
			RETURN NEW;
		END IF;
	END IF;

	-- patient of this intake regimen
	SELECT fk_patient INTO _identity_from_regimen FROM clin.encounter where pk = NEW.fk_encounter;
	-- patient of linked substance intake
	SELECT fk_patient INTO _identity_from_intake FROM clin.encounter where pk = (
		select fk_encounter from clin.intake where pk = NEW.fk_intake
	);

	IF _identity_from_regimen = _identity_from_intake THEN
		RETURN NEW;
	END IF;

	RAISE EXCEPTION
		''INSERT/UPDATE into %.%: Sanity check failed. Regimen % patient = %. Intake % patient = %.'',
			TG_TABLE_SCHEMA,
			TG_TABLE_NAME,
			NEW.pk,
			_identity_from_regimen,
			NEW.fk_intake,
			_identity_from_intake
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
end;';


create trigger tr_chck_pat_from_intake_vs_regimen
	before insert or update
	on clin.intake_regimen
	for each row
		execute procedure clin.trf_chck_pat_from_intake_vs_regimen();

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-trf_chck_pat_from_intake_vs_regimen.sql', '23.0');
