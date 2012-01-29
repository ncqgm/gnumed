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
-- .fk_receiver_identity
comment on column bill.bill.fk_receiver_identity is 'link to the receiver as a GNUmed identity, if known';

alter table bill.bill
	alter column fk_receiver_identity
		set default NULL;

\unset ON_ERROR_STOP
alter table bill.bill.fk_receiver_identity drop constraint bill_fk_receiver_identity_fkey cascade;
\set ON_ERROR_STOP 1

alter table bill.bill
	add foreign key (fk_receiver_identity)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

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
\unset ON_ERROR_STOP
drop view bill.v_bills cascade;
\set ON_ERROR_STOP 1

create or replace view bill.v_bills as

SELECT
	b_b.pk
		as pk_bill,
	b_b.receiver_address,
	b_b.fk_receiver_identity
		as pk_receiver_identity,
	-- assumes that all bill_items have the same currency
	(select sum(final_amount) from bill.v_bill_items where pk_bill = b_b.pk)
		as total_amount,
	-- assumes that all bill_items have the same currency
	(select currency from bill.v_bill_items where pk_bill = b_b.pk limit 1)
		as currency,
	b_b.payment_method,
	b_b.close_date,
	-- assumes all bill items point to encounters of one patient
	(select fk_patient from clin.encounter where clin.encounter.pk = (
		select fk_encounter from bill.bill_item where fk_bill = b_b.pk limit 1
	))	as pk_patient,
	(select array_agg(bill.bill_item.pk) from bill.bill_item where fk_bill = b_b.pk)
		as pk_bill_items,
	(select array_agg(bill.v_bill_items.currency) from bill.v_bill_items where pk_bill = b_b.pk limit 1)
		as item_currencies
FROM
	bill.bill b_b
;

grant select on bill.v_bills to group "gm-doctors";


\unset ON_ERROR_STOP
insert into bill.bill (receiver_address) values ('Federation Health Fund');
update bill.bill_item set fk_bill = currval('bill.bill_item_pk_seq') where fk_bill is NULL and description = 'Reiseberatung';
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-bill-dynamic.sql', '17.0');
