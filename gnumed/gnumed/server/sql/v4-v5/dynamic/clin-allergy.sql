-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v4
-- Target database version: v5
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-allergy.sql,v 1.1 2007-03-18 13:37:47 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
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
		select into _no_of_allergies count(1) from clin.v_pat_allergies where pk_patient = _fk_patient;
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
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-allergy.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-allergy.sql,v $
-- Revision 1.1  2007-03-18 13:37:47  ncq
-- - add trigger to sync allergic state to allergy content
--
--
