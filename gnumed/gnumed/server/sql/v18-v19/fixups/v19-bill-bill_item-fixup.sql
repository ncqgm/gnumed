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
-- .fk_bill
\unset ON_ERROR_STOP
alter table bill.bill_item drop constraint bill_item_fk_bill_fkey cascade;
alter table bill.bill_item drop constraint FK_bill_item_fk_bill cascade;
\set ON_ERROR_STOP 1

alter table bill.bill_item
	add constraint FK_bill_item_fk_bill
		foreign key (fk_bill)
		references bill.bill(pk)
		on update cascade
		on delete set null
		deferrable initially deferred
;

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
		if OLD.fk_bill IS NULL then
			return NULL;
		end if;
		if OLD.fk_bill IS NOT DISTINCT FROM NEW.fk_bill then
			return NULL;
		end if;
	else
		if OLD.fk_bill is NULL then
			return NULL;
		end if;
	end if;

	-- we now either:
	--	DELETE with .fk_bill NOT NULL
	-- or:
	--	UPDATE with an .fk_bill change (including towards fk_bill = NULL)

	-- let us check whether the (previous) bill still exists
	-- at all or whether we are deleting the bill (and thereby
	-- setting our .fk_bill to NULL)
	-- only works at or below REPEATABLE READ after deletion of bill
	perform 1 from bill.bill where pk = OLD.fk_bill;
	if FOUND is FALSE then
		return NULL;
	end if;

	select count(1) into _item_count
	from bill.bill_item
	where
		fk_bill = OLD.fk_bill
			and
		pk != OLD.pk;

	if _item_count > 0 then
		return NULL;
	end if;

	_msg := ''[bill.trf_prevent_empty_bills]: cannot remove (by ''
			|| ''<'' || TG_OP || ''>''
			||'') the only item (bill.bill_item.pk=''
			|| coalesce(OLD.pk::text, ''<NULL>''::text)
			|| '') from bill (bill.bill_item.fk_bill=bill.bill.pk=''
			|| coalesce(OLD.fk_bill::text, ''<NULL>''::text)
			|| '') '';
	raise exception unique_violation using message = _msg;

	return NULL;
END;';


comment on function bill.trf_prevent_empty_bills() is
	'Prevent bills to become void of items due to deletions/updates of bill items.';


\unset ON_ERROR_STOP
drop trigger tr_prevent_empty_bills on bill.bill_item cascade;
\set ON_ERROR_STOP 1

create constraint trigger tr_prevent_empty_bills
	after update or delete on bill.bill_item
	deferrable initially deferred
	for each row execute procedure bill.trf_prevent_empty_bills()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-bill-bill_item-fixup.sql', '19.12');
