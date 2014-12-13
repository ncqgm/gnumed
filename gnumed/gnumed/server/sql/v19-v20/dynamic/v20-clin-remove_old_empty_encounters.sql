-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
create or replace function clin.remove_old_empty_encounters(integer, interval)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_pk_identity alias for $1;
	_defined_minimum_encounter_age alias for $2;
	_usable_minimum_encounter_age interval;
	_encounter_count integer;
BEGIN
	-- does person exist ?
	perform 1 from dem.identity where pk = _pk_identity;
	if not found then
		raise exception ''clin.remove_old_empty_encounters(person=%, min_age=%): person [%] does not exist'', _pk_identity, _defined_minimum_encounter_age, _pk_identity;
		return false;
	end if;

	SELECT count(1) INTO STRICT _encounter_count
	FROM clin.encounter
	WHERE fk_patient = _pk_identity;
	IF _encounter_count < 2 THEN
		raise exception ''clin.remove_old_empty_encounters(person=%, min_age=%): there are less than 2 encounters for this patient'', _pk_identity, _defined_minimum_encounter_age;
		return false;
	END IF;

	if _defined_minimum_encounter_age < ''3 days''::interval then
		_usable_minimum_encounter_age := ''3 days''::interval;
	else
		_usable_minimum_encounter_age := _defined_minimum_encounter_age;
	end if;

	DELETE FROM clin.encounter WHERE
		clin.encounter.fk_patient = _pk_identity
			AND
		age(clin.encounter.last_affirmed) > _usable_minimum_encounter_age
			AND
		NOT EXISTS (SELECT 1 FROM clin.clin_root_item WHERE fk_encounter = clin.encounter.pk)
			AND
		NOT EXISTS (SELECT 1 FROM blobs.doc_med WHERE fk_encounter = clin.encounter.pk)
			AND
		NOT EXISTS (SELECT 1 FROM clin.episode WHERE fk_encounter = clin.encounter.pk)
			AND
		NOT EXISTS (SELECT 1 FROM clin.health_issue WHERE fk_encounter = clin.encounter.pk)
			AND
		NOT EXISTS (SELECT 1 FROM clin.allergy_state WHERE fk_encounter = clin.encounter.pk)
			AND
		NOT EXISTS (SELECT 1 FROM bill.bill_item WHERE fk_encounter = clin.encounter.pk)
			AND
		NOT EXISTS (SELECT 1 FROM clin.external_care WHERE fk_encounter = clin.encounter.pk)
			AND
		NOT EXISTS (SELECT 1 FROM clin.suppressed_hint WHERE fk_encounter = clin.encounter.pk)
	;

	return true;
END;';

comment on function clin.remove_old_empty_encounters(integer, interval) is
	'Remove empty encountersolder than a definable minimum age from a patient.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-remove_old_empty_encounters.sql', '20.0');
