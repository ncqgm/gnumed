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
comment on table ref.billable is 'items that *can* be billed to patients';

select audit.register_table_for_auditing('ref'::name, 'billable'::name);
select gm.register_notifying_table('ref', 'billable');


grant select on
	ref.billable
to group "gm-public";

grant usage on
	ref.billable_pk_seq
to group "gm-public";


\unset ON_ERROR_STOP
drop index idx_ref_billable_code_unique_per_system cascade;
drop index idx_ref_billable_term_unique_per_system cascade;
\set ON_ERROR_STOP 1

create unique index idx_ref_billable_code_unique_per_system on ref.billable(fk_data_source, lower(code));
create unique index idx_ref_billable_term_unique_per_system on ref.billable(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
-- .fk_data_source
\unset ON_ERROR_STOP
alter table ref.billable drop constraint billable_fk_data_source_fkey cascade;
\set ON_ERROR_STOP 1

alter table ref.billable
	alter column fk_data_source
		set not null;

alter table ref.billable
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;


\unset ON_ERROR_STOP
drop index idx_ref_billable_fk_data_src cascade;
\set ON_ERROR_STOP 1

create index idx_ref_billable_fk_data_src on ref.billable(fk_data_source);

-- --------------------------------------------------------------
-- .amount
comment on column ref.billable.amount is 'How much to bill for this item.';

alter table ref.billable
	alter column amount
		set not null;

alter table ref.billable
	alter column amount
		set default 0;

alter table ref.billable
	add constraint ref_billable_sane_amount check
		(amount >= 0);

-- --------------------------------------------------------------
-- .currency
comment on column ref.billable.currency is 'The currency .amount is in.';

alter table ref.billable
	alter column currency
		set default 'EUR';

alter table ref.billable
	add constraint ref_billable_sane_currency check
		(gm.is_null_or_blank_string(currency) is False);

-- --------------------------------------------------------------
-- .vat_multiplier
comment on column ref.billable.vat_multiplier is 'Multiplier to apply to .amount to calculate VAT, eg 0.19 = 19%, 0 = no VAT';

alter table ref.billable
	alter column vat_multiplier
		set not null;

alter table ref.billable
	alter column vat_multiplier
		set default 0;		-- no VAT

alter table ref.billable
	add constraint ref_billable_sane_vat_multiplier check
		(vat_multiplier >= 0);

-- --------------------------------------------------------------
-- .active
comment on column ref.billable.active is 'Whether this item is currently supposed to be used for billing patients.';

alter table ref.billable
	alter column active
		set not null;

alter table ref.billable
	alter column active
		set default True;

-- --------------------------------------------------------------
-- .discountable
comment on column ref.billable.discountable is 'Whether discounts can be applied to this item.';

alter table ref.billable
	alter column discountable
		set not null;

alter table ref.billable
	alter column discountable
		set default False;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-billable-dynamic.sql', '17.0');
