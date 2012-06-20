-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- Data contributed by: vbanait@gmail.com
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- fix trigger:

-- MUST protect from changing if in use directly or indirectly
\unset ON_ERROR_STOP
drop function ref.trf_do_not_update_substance_if_taken_by_patient() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_do_not_update_substance_if_taken_by_patient()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	-- allow for case insensitive non-changes
	if upper(OLD.description) = upper(NEW.description) then
		if OLD.amount = NEW.amount then
			if upper(OLD.unit) = upper(NEW.unit) then
				return NEW;
			end if;
		end if;
	end if;

	_msg := ''[ref.trf_do_not_update_substance_if_taken_by_patient]: as long as substance <'' || OLD.description || ''> is taken by a patient you cannot modify it'';

	perform 1 from clin.substance_intake c_si
	where c_si.fk_substance = OLD.pk
	limit 1;

	if FOUND then
		raise exception ''%'', _msg;
	end if;

	PERFORM 1
	FROM clin.substance_intake c_si
	WHERE c_si.fk_drug_component IN (
		-- get all PKs in component link table which
		-- represent the substance we want to modify
		SELECT
			r_ls2b.pk
		FROM
			ref.lnk_substance2brand r_ls2b
		WHERE
			r_ls2b.fk_substance = OLD.pk
	)
	LIMIT 1;

	if FOUND then
		raise exception ''%'', _msg;
	end if;

	return NEW;
END;';

comment on function ref.trf_do_not_update_substance_if_taken_by_patient() is
'If this substance is taken by any patient do not modify description, amount, or unit (case changes allowed).';

create trigger tr_do_not_update_substance_if_taken_by_patient
	before update
	on ref.consumable_substance
	for each row execute procedure ref.trf_do_not_update_substance_if_taken_by_patient()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-consumable_substance-trigger_fixup.sql', 'v15.11');
