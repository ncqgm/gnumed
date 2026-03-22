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

-- this was a bug:
--select audit.register_table_for_auditing('ref'::name, 'billable'::name);
select gm.register_notifying_table('ref', 'billable');


grant select on
	ref.billable
to group "gm-public";

grant usage on
	ref.billable_pk_seq
to group "gm-public";


drop index if exists idx_ref_billable_code_unique_per_system cascade;
drop index if exists idx_ref_billable_term_unique_per_system cascade;

create unique index idx_ref_billable_code_unique_per_system on ref.billable(fk_data_source, lower(code));
create unique index idx_ref_billable_term_unique_per_system on ref.billable(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
-- .fk_data_source
alter table ref.billable drop constraint if exists billable_fk_data_source_fkey cascade;

alter table ref.billable
	alter column fk_data_source
		set not null;

alter table ref.billable
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;


drop index if exists idx_ref_billable_fk_data_src cascade;

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
drop view if exists ref.v_billables cascade;

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
set standard_conforming_strings to on;

INSERT INTO ref.data_source (name_long, name_short, version, source) values ('Gebührenordnung für Ärzte', 'GOÄ', '1996', 'BÄK')
	on conflict do nothing;

INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('1', 'Beratung, auch telefonisch', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 4.66, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('4', 'Erhebung Fremdanamnese und/oder Unterweisung/Führung Bezugsperson(en)', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 12.82, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('5', 'symptombezogene Untersuchung', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 4.66, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('A', 'Zuschlag Untersuchung, außerhalb der Sprechstunde', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 4.08, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('B', 'Zuschlag Untersuchung, außerhalb der Sprechstunde, 20-22 o. 6-8 Uhr', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 10.49, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('C', 'Zuschlag Untersuchung, 22-6 Uhr', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 18.65, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('D', 'Zuschlag Untersuchung, Sa/So/Feiertag', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 12.82, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('K1', 'Zuschlag Untersuchung, Kind bis vollendetes 4.LJ', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 6.99, U&'\20AC', 0.19) on conflict do nothing;

INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('50', 'Besuch, einschl.Beratung und symtombezog.Untersuchung', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 18.65, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('55', 'Begleitung Patient durch Arzt zur unmittelbar notw.stat.Behandlung, ggf.mit Organisation der Einweisung', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 29.14, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('E', 'Zuschlag Besuch, dringend angefordert, unverzüglich ausgeführt', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 9.33, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('F', 'Zuschlag Besuch, 20-22 o. 6-8 Uhr', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 15.15, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('G', 'Zuschlag Besuch, 22-6 Uhr', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 26.23, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('H', 'Zuschlag Besuch, Sa/So/Feiertag', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 19.82, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('K2', 'Zuschlag Besuch, Kind bis vollendetes 4.LJ', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 6.99, U&'\20AC', 0.19) on conflict do nothing;

INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('75', 'ausführlicher Befundbericht', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 7.58, U&'\20AC', 0.19) on conflict do nothing;

INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('100', 'Leichenschau mit Totenschein', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 14.57, U&'\20AC', 0.19) on conflict do nothing;

INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('250', 'Blutentnahme, venös', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 2.33, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('252', 'Injektion, s.c./s.m./i.c./i.m.', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 2.33, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('253', 'Injektion, i.v.', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 4.08, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('265', 'Portspülung', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 3.50, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('266', 'intrakutane Quaddelung (pro Sitzung)', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 3.50, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('270', 'Infusion, s.c.', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 4.66, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('271', 'Infusion, i.v., bis 30 Minuten', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 6.99, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('272', 'Infusion, i.v., ab 30 Minuten', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 10.49, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('273', 'Infusion, i.v., Kind bis vollendetes 4.LJ', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 10.49, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('303', 'Punktion, Drüse/Schleimbeutel/Ganglion/Serom/Hygrom/Hämatom/Abszeß o. oberflächl.Körperteil', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 4.66, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('500', 'Inhalation, auch mittels Vernebler', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 2.21, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('601', 'Hyperventilationsprüfung', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 2.56, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('602', 'Pulsoxymetrie', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 8.86, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('650', 'Rhythmus-EKG', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 8.86, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('651', 'Ruhe-EKG (mindestens 9 Ableitungen)', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 14.75, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('3511', 'Schnelltest (Glucose, CRP, Urin, Troponin, D-Dimer, ASL)', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 2.91, U&'\20AC', 0.19) on conflict do nothing;

INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('2000', 'Kleine Wunde, Erstversorgung', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 4.08, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('2003', 'Große und/oder stark verunreinigte Wunde, Erstversorgung', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 7.58, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('2008', 'Wund- oder Fistelspaltung', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 5.25, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('2009', 'Fremdkörperentfernung, fühlbar, oberflächlich', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 5.83, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('2205', 'Einrenkung, Finger- oder Zehengelenk (nicht Daumen)', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 5.42, U&'\20AC', 0.19) on conflict do nothing;
INSERT INTO ref.billable (code, term, fk_data_source, amount, currency, vat_multiplier) values ('2207', 'Einrenkung, Daumengelenk', (select pk from ref.data_source where name_long = 'Gebührenordnung für Ärzte' and name_short = 'GOÄ' and version = '1996' and source = 'BÄK'), 8.63, U&'\20AC', 0.19) on conflict do nothing;

reset standard_conforming_strings;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-billable-dynamic.sql', '17.0');
