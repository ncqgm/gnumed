-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v8
-- Target database version: v9
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-allergy-dynamic.sql,v 1.1 2008-08-15 15:54:25 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function clin.trf_sync_allergic_state_on_allergies_modified() cascade;
\set ON_ERROR_STOP 1


create function clin.trf_sync_allergic_state_on_allergies_modified()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_fk_patient integer;
	_state integer;
	_no_of_allergies integer;
BEGIN
	if TG_OP = ''INSERT'' then
		select into _fk_patient fk_patient from clin.encounter where pk = NEW.fk_encounter;
		_state := 1;
	end if;

	if TG_OP = ''DELETE'' then
		-- only run this trigger if deleting last allergy
		select into _fk_patient fk_patient from clin.encounter where pk = OLD.fk_encounter;
		select into _no_of_allergies count(1) from clin.allergy where fk_encounter in (
			select pk from clin.encounter where fk_patient = _fk_patient
		);
		if _no_of_allergies > 1 then
			return OLD;		-- still allergies left
		end if;
		_state := NULL;
	end if;

	update clin.allergy_state
		set has_allergy = _state
		where fk_patient = _fk_patient;

	if not FOUND then
		insert into clin.allergy_state
			(fk_patient, has_allergy)
		values
			(_fk_patient, _state);
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
select gm.log_script_insertion('$RCSfile: v9-clin-allergy-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-allergy-dynamic.sql,v $
-- Revision 1.1  2008-08-15 15:54:25  ncq
-- - fix trigger function
--
--
