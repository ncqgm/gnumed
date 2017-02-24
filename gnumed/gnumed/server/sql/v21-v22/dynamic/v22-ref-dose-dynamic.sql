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
-- 400 mg / 1 Tablette -> 400 mg / NULL
-- 250 mg / 5 ml Saft -> 50 mg / (1) ml
-- 4% = 4 g / 100 ml Saft -> 4000 mg / 100 ml -> 40 mg / (1) ml

-- table
comment on table ref.dose is 'Links doses to consumable substances.';

select audit.register_table_for_auditing('ref', 'dose');
select gm.register_notifying_table('ref', 'dose');

-- table constraints
drop index if exists ref.idx_dose_uniq_row cascade;
create unique index idx_dose_uniq_row on ref.dose(fk_substance, amount, unit, dose_unit);

-- grants
grant select on ref.dose to "gm-public";
grant insert, update, delete on ref.dose to "gm-doctors";
grant usage on ref.dose_pk_seq to "gm-public";

-- --------------------------------------------------------------
-- .fk_substance
comment on column ref.dose.fk_substance is 'FK linking the substance';

alter table ref.dose
	alter column fk_substance
		set not null;

alter table ref.dose drop constraint if exists ref_dose_fk_substance cascade;

alter table ref.dose
	add constraint ref_dose_fk_substance
		foreign key (fk_substance) references ref.substance(pk)
			on update cascade
			on delete restrict
;

-- --------------------------------------------------------------
-- .amount
comment on column ref.dose.amount is 'the amount of substance (the "5" in "5mg/ml")';

alter table ref.dose drop constraint if exists ref_dose_sane_amount cascade;

alter table ref.dose
	alter column amount
		set not null;

alter table ref.dose
	add constraint ref_dose_sane_amount check (
		amount > 0
	);

-- --------------------------------------------------------------
-- .unit
comment on column ref.dose.unit is 'unit of amount (the "mg" in "5mg/ml")';

alter table ref.dose
	alter column unit
		set not null;

alter table ref.dose drop constraint if exists ref_dose_sane_unit cascade;

alter table ref.dose
	add constraint ref_dose_sane_unit check (
		gm.is_null_or_blank_string(unit) is False
	);

-- --------------------------------------------------------------
-- .dose_unit
comment on column ref.dose.dose_unit is 'unit of reference amount,
 IOW the "ml" in "5mg/ml" (the reference amount is always assumed to be 1, as in "5mg/1ml"),
 if NULL the unit is "1 delivery unit (tablet, capsule, suppository, sachet, ...)",
 corresponds to "dose unit" in UCUM or "unit of product usage" in SNOMED';

alter table ref.dose drop constraint if exists ref_dose_sane_dose_unit cascade;

alter table ref.dose
	add constraint ref_dose_sane_dose_unit check (
		gm.is_null_or_non_empty_string(dose_unit) is True
	);

-- --------------------------------------------------------------
-- populate
insert into ref.dose (fk_substance, amount, unit)
	select
		(select pk from ref.substance where description = r_cs.description),
		r_cs.amount,
		r_cs.unit
	from
		ref.consumable_substance r_cs
	where
		not exists (
			select 1 from ref.dose r_d
			where
				r_d.fk_substance = (select pk from ref.substance r_s where r_s.description = r_cs.description)
					and
				r_d.amount = r_cs.amount
					and
				r_d.unit = r_cs.unit
		)
;

-- --------------------------------------------------------------
drop view if exists ref.v_substance_doses cascade;

create view ref.v_substance_doses as
select
	r_d.pk as pk_dose,
	r_vs.substance,
	r_d.amount,
	r_d.unit,
	r_d.dose_unit,
	r_vs.intake_instructions,
	r_vs.atc as atc_substance,
	r_vs.loincs,

	r_vs.pk_substance,
	r_d.xmin as xmin_dose
from
	ref.dose r_d
		inner join ref.v_substances r_vs on (r_d.fk_substance = r_vs.pk_substance)
--		inner join ref.substance r_s on (r_d.fk_substance = r_s.pk)
;

grant select on ref.v_substance_doses to "gm-public";

-- --------------------------------------------------------------
drop function if exists ref.trf_upd_assert_dose_unit_in_multi_component_drugs() cascade;

create or replace function ref.trf_upd_assert_dose_unit_in_multi_component_drugs()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_drug_product integer;
	_component_count integer;
	_dose_unit_count integer;
	_msg text;
BEGIN
	SELECT fk_drug_product into strict _pk_drug_product
	FROM ref.lnk_dose2drug
	WHERE fk_dose = NEW.pk;

	if FOUND IS FALSE then
		return NEW;
	end if;

	SELECT count(1) into strict _component_count
	FROM ref.lnk_dose2drug
	WHERE fk_drug_product = _pk_drug_product;

	if _component_count = 1 then
		return NEW;
	end if;

	SELECT count(1) into strict _dose_unit_count
	FROM (
		SELECT dose_unit
		FROM ref.v_drug_components
		WHERE pk_drug_product = _pk_drug_product
		GROUP BY dose_unit
	) AS dose_unit_count;

	if _dose_unit_count = 1 then
		return NEW;
	end if;

	_msg := ''[ref.trf_upd_assert_dose_unit_in_multi_component_drugs()]: cannot change <dose_unit> on dose ['' || NEW.pk || ''] ''
		|| ''from ['' || coalesce(OLD.dose_unit, ''<NULL>'') || ''] ''
		|| ''to ['' || coalesce(NEW.dose_unit, ''<NULL>'') || ''] ''
		|| ''because all doses linked to drug product ['' || _pk_drug_product || ''] ''
		|| ''must have the same <dose_unit>'';
	raise exception check_violation using message = _msg;

	return NEW;
END;';


comment on function ref.trf_upd_assert_dose_unit_in_multi_component_drugs() is
	'Assert that after updates to ref.dose.dose_unit all substance doses linked into a multi-component drug still carry the same <dose_unit>.';


create constraint trigger tr_upd_assert_dose_unit_in_multi_component_drugs
	after update on ref.dose
	deferrable initially deferred
	for each row when (
		(NEW.dose_unit IS DISTINCT FROM OLD.dose_unit)
	)
	execute procedure ref.trf_upd_assert_dose_unit_in_multi_component_drugs();

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-dose-dynamic.sql', '22.0');
