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
-- .invoice_id
comment on column bill.bill.invoice_id is 'the ID of the bill';

\unset ON_ERROR_STOP
alter table bill.bill drop constraint bill_bill_sane_invoice_id;
alter table bill.bill drop constraint bill_bill_uniq_invoice_id cascade;
\set ON_ERROR_STOP 1

alter table bill.bill
	add constraint bill_bill_sane_invoice_id check (
		gm.is_null_or_blank_string(invoice_id) is False
	);

alter table bill.bill
	add constraint bill_bill_uniq_invoice_id
		unique(invoice_id);

-- --------------------------------------------------------------
-- .close_date
comment on column bill.bill.close_date is 'cannot add further bill_items after this date if not NULL';

alter table bill.bill
	alter column close_date
		set default NULL;

-- --------------------------------------------------------------
comment on column bill.bill.apply_vat is 'whether or not to apply VAT on the invoice';

alter table bill.bill
	alter column apply_vat
		set default True;

alter table bill.bill
	alter column apply_vat
		set not NULL;

-- --------------------------------------------------------------
-- .fk_receiver_identity
comment on column bill.bill.fk_receiver_identity is 'link to the receiver as a GNUmed identity, if known';

alter table bill.bill
	alter column fk_receiver_identity
		set default NULL;

\unset ON_ERROR_STOP
alter table bill.bill drop constraint bill_fk_receiver_identity_fkey cascade;
\set ON_ERROR_STOP 1

alter table bill.bill
	add foreign key (fk_receiver_identity)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
-- .fk_receiver_address
comment on column bill.bill.fk_receiver_address is 'links the address of the receiver of the invoice';

\unset ON_ERROR_STOP
alter table bill.bill drop constraint bill_fk_receiver_address_fkey cascade;
\set ON_ERROR_STOP 1

alter table bill.bill
	add foreign key (fk_receiver_address)
		references dem.lnk_person_org_address(id)
		on update cascade
		on delete restrict;


\unset ON_ERROR_STOP
alter table bill.bill drop constraint bill_bill_sane_recv_adr cascade;
\set ON_ERROR_STOP 1

alter table bill.bill
	add constraint bill_bill_sane_recv_adr check (
		(fk_receiver_address is not null)
			or
		(close_date is NULL)
	);

-- --------------------------------------------------------------
-- .fk_doc
comment on column bill.bill.fk_doc is 'links to the document which contains the invoice PDF';

\unset ON_ERROR_STOP
alter table bill.bill drop constraint bill_fk_doc_fkey cascade;
\set ON_ERROR_STOP 1

alter table bill.bill
	add foreign key (fk_doc)
		references blobs.doc_med(pk)
		on update cascade
		on delete set null;

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


\unset ON_ERROR_STOP
insert into bill.bill (invoice_id) values ('GNUmed@Enterprise-2012-1');
update bill.bill_item set fk_bill = currval('bill.bill_item_pk_seq') where fk_bill is NULL and description = 'Reiseberatung';
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view bill.v_export4accounting cascade;
\set ON_ERROR_STOP 1

create or replace view bill.v_export4accounting as

select
	me.*,
	'Rg. '::text || me.invoice_id
		|| ' vom '::text || me.value_date
		|| ', KdNr. '::text || coalesce(me.pk_receiver_identity::text, '<?>')
	as description
from (
		SELECT
			b_vb.pk_bill,
			'Income'::text
				AS account,
			b_vb.invoice_id,
			b_vb.pk_receiver_identity,
			b_vb.close_date
				AS value_date,
			- b_vb.total_amount
				AS amount,
			b_vb.currency
		FROM
			bill.v_bills b_vb
		WHERE
			b_vb.close_date is not NULL

		UNION ALL

		SELECT
			b_vb.pk_bill,
			'Debitor '::text || coalesce(b_vb.pk_receiver_identity::text, '<?>')
				as account,
			b_vb.invoice_id,
			b_vb.pk_receiver_identity,
			b_vb.close_date
				AS value_date,
			b_vb.total_amount
				as amount,
			b_vb.currency
		FROM
			bill.v_bills b_vb
		WHERE
			b_vb.close_date is not NULL
) as me;


GRANT SELECT ON TABLE bill.v_export4accounting TO "gm-staff";
GRANT SELECT ON TABLE bill.v_export4accounting TO "gm-doctors";
GRANT SELECT ON TABLE bill.v_export4accounting TO "gm-dbo";

-- --------------------------------------------------------------
create or replace function bill.get_bill_receiver_identity(integer)
	returns integer
	LANGUAGE SQL
	AS '
select
	value
from (
	select
		id.pk_id,
		id.value::integer
	from
		dem.v_external_ids4identity id
			join dem.identity d_i on (id.value = d_i.pk::text)
	where
		id.pk_type = (select pk from dem.enum_ext_id_types where name = ''bill receiver'' and issuer = ''GNUmed'')
			and
		id.pk_identity = $1

	union all

	select
		0,
		$1
) me
limit 1;';

select dem.add_external_id_type('bill receiver', 'GNUmed');
select i18n.upd_tx('de', 'bill receiver', 'Rechnungsempfänger');

-- --------------------------------------------------------------
select setval('dem.address_type_id_seq', (select count(1) from dem.address_type));

\unset ON_ERROR_STOP
insert into dem.address_type (name) values ('billing');
\set ON_ERROR_STOP 1

select i18n.upd_tx('de', 'billing', 'Rechnungsanschrift');
select i18n.upd_tx('de', 'invoice', 'Rechnungsbeleg');

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-bill-dynamic.sql', '17.0');
