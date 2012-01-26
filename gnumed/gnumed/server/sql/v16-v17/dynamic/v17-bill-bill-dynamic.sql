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
comment on table bill.bill is 'actual bills';

select audit.register_table_for_auditing('bill', 'bill');
select gm.register_notifying_table('bill', 'bill');

grant select, insert, delete, update on
	bill.bill
to group "gm-doctors";

grant select on
	bill.bill
to group "gm-public";

grant usage on
	bill.bill_pk_seq
to group "gm-public";

-- --------------------------------------------------------------
-- .payment_method
comment on column bill.bill.payment_method is 'the method the customer is supposed to pay by';

alter table bill.bill
	alter column payment_method
		set default 'cash'::text;

\unset ON_ERROR_STOP
alter table bill.bill drop constraint bill_bill_sane_pay_method;
\set ON_ERROR_STOP 1

alter table bill.bill
	add constraint bill_bill_sane_pay_method check
		(gm.is_null_or_blank_string(payment_method) is False);

-- --------------------------------------------------------------
-- .close_date
comment on column bill.bill.close_date is 'cannot add further bill_items after this date if not NULL';

alter table bill.bill
	alter column close_date
		set default NULL;

-- --------------------------------------------------------------
-- .receiver_address
comment on column bill.bill.receiver_address is 'the address of the receiver of the invoice, retrieved at close time';

\unset ON_ERROR_STOP
alter table bill.bill drop constraint bill_bill_sane_recv_adr;
\set ON_ERROR_STOP 1

alter table bill.bill
	add constraint bill_bill_sane_recv_adr check (
		(close_date is NULL)
		-- nice but not safe:
		--or (close_date > now())
			or
		(gm.is_null_or_blank_string(receiver_address) is False)
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-bill-dynamic.sql', '17.0');
