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


-- .description
comment on column bill.bill_item.description is
	'Can be used to further explain the bill item over and above .fk_billable.description.';

\unset ON_ERROR_STOP
alter table bill.bill_item drop constraint desc_not_empty;
alter table bill.bill_item drop constraint bill_bill_item_sane_desc;
\set ON_ERROR_STOP 1

alter table bill.bill_item
	add constraint bill_bill_item_sane_desc check
		(gm.is_null_or_non_empty_string(description) is True);


-- .net_amount_per_unit
comment on column bill.bill_item.net_amount_per_unit is
	'How much to charge for one unit of this bill item. If NULL use .fk_billable.amount.';


-- .currency
comment on column bill.bill_item.currency is
	'Which currency to charge in. Must not be NULL if .net_amount_per_unit is not NULL.';


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
drop index idx_bill_bill_item_fk_billable cascade;
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
drop index idx_bill_bill_item_fk_bill cascade;
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
select gm.log_script_insertion('v17-bill-bill_item-dynamic.sql', '17.0');
