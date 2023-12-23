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
-- we now take *absence* of an allergy_state row to mean no
-- data has been obtained so far, previously this was designated
-- by a row with has_allergy=NULL
--
-- so remove entries with has_allergy = NULL
DELETE FROM clin.allergy_state c_as WHERE c_as.has_allergy IS NULL;

-- and update entries with -1 to NULL
UPDATE clin.allergy_state
SET has_allergy = NULL
WHERE has_allergy = -1;

-- --------------------------------------------------------------
drop function if exists clin.trf_sync_allergic_state_on_allergies_modified() cascade;


create function clin.trf_sync_allergic_state_on_allergies_modified()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_fk_patient integer;
	_fk_encounter integer;
	_state integer;
	_no_of_allergies integer;
BEGIN
	if TG_OP = ''DELETE'' then
		-- only run this trigger if deleting last allergy
		select into _fk_patient fk_patient from clin.encounter where pk = OLD.fk_encounter;
		select into _no_of_allergies count(1) from clin.allergy where fk_encounter in (
			select pk from clin.encounter where fk_patient = _fk_patient
		);
		if _no_of_allergies > 1 then
			return OLD;		-- still allergies left
		end if;
		_fk_encounter := OLD.fk_encounter;
		-- deleting the last allergy does not mean we know there IS no allergy, so assume NULL
		_state := NULL::INTEGER;
	end if;

	if TG_OP = ''INSERT'' then
		select into _fk_patient fk_patient from clin.encounter where pk = NEW.fk_encounter;
		_fk_encounter := NEW.fk_encounter;
		_state := 1;
	end if;

	update clin.allergy_state
		set
			has_allergy = _state,
			last_confirmed = coalesce(last_confirmed, now())
		where fk_encounter in (
			select pk from clin.encounter where fk_patient = _fk_patient
		);

	if not FOUND then
		insert into clin.allergy_state
			(fk_encounter, has_allergy, last_confirmed)
		values
			(_fk_encounter, _state, now());
	end if;

	return NEW;
END;';

comment on function clin.trf_sync_allergic_state_on_allergies_modified() is
	'trigger function to sync the allergy state on insert/delete';


create trigger tr_sync_allergic_state_on_allergies_modified
	after insert or delete on clin.allergy
	for each row execute procedure clin.trf_sync_allergic_state_on_allergies_modified()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-allergy_state-dynamic.sql', '23.0');
