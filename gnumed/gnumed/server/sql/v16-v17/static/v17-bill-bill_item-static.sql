-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table bill.bill_item
	add column fk_billable integer;

alter table bill.bill_item
	add column fk_bill integer;

alter table bill.bill_item
	add column unit_count integer;

alter table bill.bill_item
	add column amount_multiplier numeric;

alter table bill.bill_item
	rename column amount_to_bill to net_amount_per_unit;

alter table bill.bill_item
	drop column code;

alter table bill.bill_item
	drop column system;

alter table bill.bill_item
	drop column locale;

alter table bill.bill_item
	drop column receiver;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-bill_item-static.sql', '17.0');
