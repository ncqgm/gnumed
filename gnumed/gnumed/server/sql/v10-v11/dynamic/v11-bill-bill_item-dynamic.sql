-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-bill-bill_item-dynamic.sql,v 1.3 2009-06-04 16:36:46 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on schema bill is 'Holds everything related to billing.';

-- --------------------------------------------------------------
comment on table bill.bill_item is
'Holds items ready for being billed.';

select gm.add_table_for_notifies('bill', 'bill_item');



comment on column bill.bill_item.fk_provider is
'by whom or on whose behalf did the billable activity happen';

alter table bill.bill_item
	alter column fk_provider
		set not null;



comment on column bill.bill_item.fk_encounter is
'the encounter during which the billable action for this item took place';

alter table bill.bill_item
	alter column fk_encounter
		set not null;



comment on column bill.bill_item.date_to_bill is
'the date under which this item is to be billed';

alter table bill.bill_item
	alter column date_to_bill
		set not null;

alter table bill.bill_item
	alter column date_to_bill
		set default current_date;



comment on column bill.bill_item.code is
'a code for the billing item';

alter table bill.bill_item
	add constraint code_not_empty check (
		gm.is_null_or_non_empty_string(code)
	)
;



comment on column bill.bill_item.system is
'the coding system for the code for the billing item';

alter table bill.bill_item
	add constraint system_not_empty_if_code check (
		(code is null)
			or
		(system is not null)
	)
;



comment on column bill.bill_item.description is
'a human comprehensible description of the item';

alter table bill.bill_item
	add constraint desc_not_empty check (
		gm.is_null_or_blank_string(description) is False
	)
;



comment on column bill.bill_item.receiver is
'who is to receive the bill';

alter table bill.bill_item
	add constraint sane_receiver check (
		gm.is_null_or_non_empty_string(description)
	)
;



comment on column bill.bill_item.amount_to_bill is
'how much to bill for this item if known';



comment on column bill.bill_item.currency is
'what currency to bill in';

alter table bill.bill_item
	add constraint currency_not_empty_if_amount check (
		(amount_to_bill is null)
			or
		(gm.is_null_or_blank_string(currency) is False)
	)
;



comment on column bill.bill_item.status is
'the status of this item';

alter table bill.bill_item
	add constraint valid_stati check (
		status in ('new', 'transferred')
	)
;

alter table bill.bill_item
	alter column status
		set default 'new';

-- --------------------------------------------------------------
grant select, insert, update, delete on
	bill.bill_item
	, bill.bill_item_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-bill-bill_item-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v11-bill-bill_item-dynamic.sql,v $
-- Revision 1.3  2009-06-04 16:36:46  ncq
-- - fix comment
--
-- Revision 1.2  2009/04/03 09:57:54  ncq
-- - add notify signal
-- - add grants
--
-- Revision 1.1  2009/03/16 15:13:03  ncq
-- - new
--
-- Revision 1.1  2009/03/10 14:29:05  ncq
-- - new
--
--