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
comment on table bill.bill_item is 'items patients currently *are* billed for';

select audit.register_table_for_auditing('bill', 'bill_item');
select gm.register_notifying_table('bill', 'bill_item');

grant select, insert, delete, update on
	bill.bill_item
to group "gm-doctors";

grant select on
	bill.bill_item
to group "gm-public";

grant usage on
	bill.bill_item_pk_seq
to group "gm-public";

-- --------------------------------------------------------------
-- .date_to_bill
comment on column bill.bill_item.date_to_bill is
	'The date the bill item was caused. If NULL, use .fk_encounter -> .started';

alter table bill.bill_item
	alter column date_to_bill
		drop not null;

alter table bill.bill_item
	alter column date_to_bill
		drop default;


-- .description
comment on column bill.bill_item.description is
	'Can be used to further explain the bill item over and above .fk_billable.description.';

\unset ON_ERROR_STOP
alter table bill.bill_item drop constraint desc_not_empty;
alter table bill.bill_item drop constraint sane_receiver;
alter table bill.bill_item drop constraint bill_bill_item_sane_desc;
\set ON_ERROR_STOP 1

alter table bill.bill_item
	add constraint bill_bill_item_sane_desc check
		(gm.is_null_or_non_empty_string(description) is True);


-- .net_amount_per_unit
comment on column bill.bill_item.net_amount_per_unit is
	'How much to charge for one unit of this bill item.';

alter table bill.bill_item
	alter column net_amount_per_unit
		set not null;

alter table bill.bill_item
	alter column net_amount_per_unit
		set default 0;


-- .currency
comment on column bill.bill_item.currency is
	'Which currency to charge in. Must not be NULL if .net_amount_per_unit is not NULL.';

alter table bill.bill_item
	alter column currency
		set not null;

\unset ON_ERROR_STOP
alter table bill.bill_item drop constraint currency_not_empty_if_amount;
alter table bill.bill_item drop constraint bill_bill_item_sane_currency;
\set ON_ERROR_STOP 1

alter table bill.bill_item
	add constraint bill_bill_item_sane_currency check
		(gm.is_null_or_blank_string(currency) is false);


-- .status


-- .fk_billable
comment on column bill.bill_item.fk_billable is
	'Links to the billable item this bill item stands for.';

alter table bill.bill_item
	alter column fk_billable
		set not null;

\unset ON_ERROR_STOP
alter table bill.bill_item drop constraint bill_item_fk_billable_fkey cascade;
\set ON_ERROR_STOP 1

alter table bill.bill_item
	add foreign key (fk_billable)
		references ref.billable(pk)
		on update cascade
		on delete restrict;


\unset ON_ERROR_STOP
drop index bill.idx_bill_bill_item_fk_billable cascade;
\set ON_ERROR_STOP 1

create index idx_bill_bill_item_fk_billable on bill.bill_item(fk_billable);


-- .fk_bill
comment on column bill.bill_item.fk_bill is
	'Links to the bill this bill item is on if any.';

\unset ON_ERROR_STOP
alter table bill.bill_item drop constraint bill_item_fk_bill_fkey cascade;
\set ON_ERROR_STOP 1

alter table bill.bill_item
	add foreign key (fk_bill)
		references bill.bill(pk)
		on update cascade
		on delete restrict;


\unset ON_ERROR_STOP
drop index bill.idx_bill_bill_item_fk_bill cascade;
\set ON_ERROR_STOP 1

create index idx_bill_bill_item_fk_bill on bill.bill_item(fk_bill);


-- .unit_count
comment on column bill.bill_item.unit_count is
	'The number of times this item is to be billed. 0 can be used for informative items.';

alter table bill.bill_item
	alter column unit_count
		set not null;

alter table bill.bill_item
	alter column unit_count
		set default 1;

\unset ON_ERROR_STOP
alter table bill.bill_item drop constraint bill_bill_item_sane_count;
\set ON_ERROR_STOP 1

alter table bill.bill_item
	add constraint bill_bill_item_sane_count check
		(unit_count > -1);


-- .amount_multiplier
comment on column bill.bill_item.amount_multiplier is
	'A multiplier to apply to .net_amount_per_unit. Can be used for discounts, rebates, or increases. Must be > 0.';

alter table bill.bill_item
	alter column amount_multiplier
		set not null;

alter table bill.bill_item
	alter column amount_multiplier
		set default 1;

\unset ON_ERROR_STOP
alter table bill.bill_item drop constraint bill_bill_item_sane_multiplier;
\set ON_ERROR_STOP 1

alter table bill.bill_item
	add constraint bill_bill_item_sane_multiplier check
		(amount_multiplier > 0);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view bill.v_bill_items cascade;
\set ON_ERROR_STOP 1

create or replace view bill.v_bill_items AS

SELECT
	b_bi.pk
		AS pk_bill_item,
	r_b.code
		AS billable_code,
	r_b.term
		AS billable_description,
	b_bi.description
		AS item_detail,
	coalesce(b_bi.date_to_bill, c_enc.started)
		AS date_to_bill,
	b_bi.net_amount_per_unit,
	b_bi.unit_count,
	b_bi.amount_multiplier,
	b_bi.unit_count * b_bi.net_amount_per_unit * b_bi.amount_multiplier
		AS total_amount,
	b_bi.unit_count * b_bi.net_amount_per_unit * b_bi.amount_multiplier * r_b.vat_multiplier
		AS vat,
	b_bi.currency,
	b_bi.date_to_bill
		AS raw_date_to_bill,
	r_b.amount
		AS billable_amount,
	r_b.vat_multiplier,
	r_b.currency
		AS billable_currency,
	r_b.comment
		AS billable_comment,
	r_b.active
		AS billable_active,
	r_b.discountable
		AS billable_discountable,
	r_ds.name_long
		AS catalog_long,
	r_ds.name_short
		AS catalog_short,
	r_ds.version
		AS catalog_version,
	r_ds.lang
		AS catalog_language,

	c_enc.fk_patient
		AS pk_patient,
	c_enc.fk_type
		AS pk_encounter_type,
	b_bi.fk_provider
		AS pk_provider,
	b_bi.fk_encounter
		AS pk_encounter_to_bill,
	b_bi.fk_bill
		AS pk_bill,
	r_b.pk
		AS pk_billable,
	r_b.fk_data_source
		AS pk_data_source,

	b_bi.xmin
		AS xmin_bill_item
FROM
	bill.bill_item b_bi
		inner join ref.billable r_b on (b_bi.fk_billable = r_b.pk)
			left join ref.data_source r_ds on (r_b.fk_data_source = r_ds.pk)
				left join clin.encounter c_enc on (b_bi.fk_encounter = c_enc.pk)
;

grant select on
	bill.v_bill_items
to group "gm-doctors";

-- --------------------------------------------------------------
set standard_conforming_strings to on;

\unset ON_ERROR_STOP
INSERT INTO bill.bill_item (
	fk_provider,
	fk_encounter,
	description,
	fk_billable,
	net_amount_per_unit,
	amount_multiplier,
	currency
) values (
	1,
	1,
	'Reiseberatung',
	1,
	25,
	2.3,
	U&'\20AC'
);
\set ON_ERROR_STOP 1

reset standard_conforming_strings;

grant usage on schema bill to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-bill_item-dynamic.sql', '17.0');
