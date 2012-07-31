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
drop function bill.trf_prevent_empty_bills() cascade;
\set ON_ERROR_STOP 1

create or replace function bill.trf_prevent_empty_bills()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_item_count integer;
	_msg text;
BEGIN
	if TG_OP = ''UPDATE'' then
		if OLD.fk_bill IS NOT DISTINCT FROM NEW.fk_bill then
			return NEW;
		end if;
	else
		if OLD.fk_bill is NULL then
			return NEW;
		end if;
	end if;

	-- we now either:
	--	DELETE with .fk_bill NOT NULL
	-- or:
	--	UPDATE with an .fk_bill change

	select count(1) into _item_count
	from bill.bill_item
	where
		fk_bill = OLD.fk_bill
			and
		pk != OLD.pk;

	if _item_count > 0 then
		if TG_OP = ''UPDATE'' then
			return NEW;
		end if;
		return OLD;
	end if;

	_msg := ''[bill.trf_prevent_empty_bills]: cannot delete the only item bill.bill_item.pk=('' || OLD.pk || '') ''
		|| ''from bill (pk='' || OLD.fk_bill || '') '';
	raise exception unique_violation using message = _msg;

	return NULL;
END;';


comment on function bill.trf_prevent_empty_bills() is
	'Prevent bills to become void of items due to deletions/updates of bill items.';

create trigger tr_prevent_empty_bills
	before update or delete on bill.bill_item
	for each row execute procedure bill.trf_prevent_empty_bills();

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-bill_item-fixup.sql', '17.2');
