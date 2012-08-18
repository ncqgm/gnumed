-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- .comment
comment on column bill.bill.comment is 'arbitrary comments on bills';

\unset ON_ERROR_STOP
alter table bill.bill drop constraint bill_bill_sane_comment;
\set ON_ERROR_STOP 1

alter table bill.bill
	add constraint bill_bill_sane_comment check (
		gm.is_null_or_non_empty_string(comment) is True
	);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view bill.v_bills cascade;
\set ON_ERROR_STOP 1

create or replace view bill.v_bills as

SELECT
	b_b.pk
		as pk_bill,
	b_b.invoice_id,
	b_b.fk_receiver_identity
		as pk_receiver_identity,
	-- assumes that all bill_items have the same currency
	(select round(sum(total_amount), 2) from bill.v_bill_items where pk_bill = b_b.pk)
		as total_amount,
	(select round(sum(vat), 2) from bill.v_bill_items where pk_bill = b_b.pk)
		as total_vat,
	(select round(sum(total_amount + vat), 2) from bill.v_bill_items where pk_bill = b_b.pk)
		as total_amount_with_vat,
	-- assumes that all bill_items have the same VAT
	(select vat_multiplier * 100 from bill.v_bill_items where pk_bill = b_b.pk limit 1)
		as percent_vat,
	-- assumes that all bill_items have the same currency
	(select currency from bill.v_bill_items where pk_bill = b_b.pk limit 1)
		as currency,
	b_b.close_date,
	b_b.apply_vat,
	b_b.comment,
	b_b.fk_receiver_address
		as pk_receiver_address,
	b_b.fk_doc
		as pk_doc,
	-- assumes all bill items point to encounters of one and the same patient
	(select fk_patient from clin.encounter where clin.encounter.pk = (
		select fk_encounter from bill.bill_item where fk_bill = b_b.pk limit 1
	))	as pk_patient,
	-- not supported by PG < 9.0
--	(select array_agg(b_vbi.pk_bill_item order by b_vbi.date_to_bill) from bill.v_bill_items b_vbi where b_vbi.pk_bill = b_b.pk)
	-- however, we can do this:
	(select array_agg(pk_bill_item) from (select b_vbi.pk_bill_item from bill.v_bill_items b_vbi where b_vbi.pk_bill = b_b.pk order by b_vbi.date_to_bill) as sorted_values)
		as pk_bill_items,
	b_b.xmin
		as xmin_bill
FROM
	bill.bill b_b
;

grant select on bill.v_bills to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-bill-bill-dynamic.sql', '18.0');
