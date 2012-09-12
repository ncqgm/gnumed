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
\unset ON_ERROR_STOP
drop function bill.trf_prevent_mislinked_bills() cascade;
\set ON_ERROR_STOP 1

create or replace function bill.trf_prevent_mislinked_bills()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_doc_patient integer;
	_bill_patient integer;
	_msg text;
BEGIN
	if NEW.fk_doc IS NULL then
		return NEW;
	end if;

	if TG_OP = ''UPDATE'' then
		if OLD.fk_doc IS NOT DISTINCT FROM NEW.fk_doc then
			return NEW;
		end if;
	end if;

	-- we now either:
	--	INSERT with .fk_doc NOT NULL
	-- or:
	--	UPDATE with an .fk_bill change to a NON-NULL value

	select pk_patient into _doc_patient
	from blobs.v_doc_med
	where
		pk_doc = NEW.fk_doc;

	select pk_patient into _bill_patient
	from bill.v_bills
	where
		pk_bill = NEW.pk;

	if _doc_patient = _bill_patient then
		return NEW;
	end if;

	_msg := ''[bill.trf_prevent_mislinked_bills]: patient mismatch between ''
		|| ''bill (pk='' || NEW.pk || '', patient='' || _bill_patient || '') ''
		|| ''and invoice (pk='' || NEW.fk_doc || '', patient='' || _doc_patient || '')'';
	raise exception integrity_constraint_violation using message = _msg;

	return NULL;
END;';


comment on function bill.trf_prevent_mislinked_bills() is
	'Prevent bills to link to invoices of another patient.';

create trigger tr_prevent_mislinked_bills
	before insert or update on bill.bill
	for each row execute procedure bill.trf_prevent_mislinked_bills();

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-bill-fixup.sql', '17.4');
