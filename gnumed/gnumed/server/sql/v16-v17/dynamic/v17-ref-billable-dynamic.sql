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
		set default E'\u20AC';

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
\unset ON_ERROR_STOP
drop view ref.v_billables cascade;
\set ON_ERROR_STOP 1

create or replace view ref.v_billables as

SELECT
	r_b.pk
		AS pk_billable,
	r_b.code
		AS billable_code,
	r_b.term
		AS billable_description,
	r_b.amount
		AS raw_amount,
	r_b.amount + (r_b.amount * r_b.vat_multiplier)
		AS amount_with_vat,
	r_b.currency
		AS currency,
	r_b.comment,
	r_b.vat_multiplier,
	r_b.active,
	r_b.discountable,
	r_ds.name_long
		AS catalog_long,
	r_ds.name_short
		AS catalog_short,
	r_ds.version
		AS catalog_version,
	r_ds.lang
		AS catalog_language,

	r_b.fk_data_source
		AS pk_data_source,
	r_b.pk_coding_system
		AS pk_coding_system_root,

	r_b.xmin
		AS xmin_billable
FROM
	ref.billable r_b
		LEFT JOIN ref.data_source r_ds ON (r_b.fk_data_source = r_ds.pk)
;

grant select on
	ref.v_billables
to group "gm-public";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
INSERT INTO ref.data_source (name_long, name_short, version, source) values ('Gebührenordnung für Ärzte', 'GOÄ', '1996', 'BÄK');
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('1', 'Beratung, auch telefonisch', currval('ref.data_source_pk_seq'), 4.66, E'\u20AC', 0.19);
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('5', 'symptombezogene Untersuchung', currval('ref.data_source_pk_seq'), 4.66, E'\u20AC', 0.19);
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('A', 'Zuschlag, außerhalb der Sprechstunde', currval('ref.data_source_pk_seq'), 4.08, E'\u20AC', 0.19);
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('B', 'Zuschlag, außerhalb der Sprechstunde, 20-22 o. 6-8 Uhr', currval('ref.data_source_pk_seq'), 10.49, E'\u20AC', 0.19);
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('C', 'Zuschlag, 22-6 Uhr', currval('ref.data_source_pk_seq'), 18.65, E'\u20AC', 0.19);
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('D', 'Zuschlag, Samstag, Sonntag, Feiertag', currval('ref.data_source_pk_seq'), 12.82, E'\u20AC', 0.19);
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('K1', 'Zuschlag, Untersuchung, Kinder bis vollendetes 4.LJ', currval('ref.data_source_pk_seq'), 6.99, E'\u20AC', 0.19);
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-billable-dynamic.sql', '17.0');
