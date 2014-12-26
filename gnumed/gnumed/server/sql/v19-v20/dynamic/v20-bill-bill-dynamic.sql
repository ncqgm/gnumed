-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table bill.bill
	alter column apply_vat
		drop not null;

alter table bill.bill
	alter column apply_vat
		set default null;

-- --------------------------------------------------------------
-- convenience, not strictly necessary
update bill.bill set
	apply_vat = NULL
where
	fk_doc IS NULL
;

alter table bill.bill drop constraint if exists bill_bill_sane_apply_vat cascade;

alter table bill.bill
	add constraint bill_bill_sane_apply_vat check (
		(apply_vat IS NOT NULL)
			OR
		((apply_vat IS NULL) AND (fk_doc IS NULL))
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-bill-bill-dynamic.sql', '20.0');
