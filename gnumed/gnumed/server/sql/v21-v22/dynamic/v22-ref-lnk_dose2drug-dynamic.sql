-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
-- table
comment on table ref.lnk_dose2drug is 'Links doses to drug products';

select audit.register_table_for_auditing('ref', 'lnk_dose2drug');
select gm.register_notifying_table('ref', 'lnk_dose2drug');

-- table constraints
drop index if exists ref.idx_ld2d_dose_uniq_per_drug_product cascade;
create unique index idx_ld2d_dose_uniq_per_drug_product on ref.lnk_dose2drug(fk_dose, fk_drug_product);

-- grants
grant select on ref.lnk_dose2drug to "gm-public";
grant insert, update, delete on ref.lnk_dose2drug to "gm-doctors";
grant usage on ref.lnk_dose2drug_pk_seq to "gm-public";

-- --------------------------------------------------------------
-- .fk_dose
comment on column ref.lnk_dose2drug.fk_dose is 'FK linking the dose';

alter table ref.lnk_dose2drug
	alter column fk_dose
		set not null;

alter table ref.lnk_dose2drug drop constraint if exists ref_ld2d_fk_dose cascade;

alter table ref.lnk_dose2drug
	add constraint ref_ld2d_fk_dose
		foreign key (fk_dose) references ref.dose(pk)
			on update cascade
			on delete restrict
;

-- --------------------------------------------------------------
-- .fk_drug_product
comment on column ref.lnk_dose2drug.fk_drug_product is 'FK linking the drug product';

alter table ref.lnk_dose2drug
	alter column fk_drug_product
		set not null;

alter table ref.lnk_dose2drug drop constraint if exists ref_ld2d_fk_drug_product cascade;

alter table ref.lnk_dose2drug
	add constraint ref_ld2d_fk_drug_product
		foreign key (fk_drug_product) references ref.drug_product(pk)
			on update cascade
			on delete cascade
;

-- --------------------------------------------------------------
-- create dose/drug links for existing drug products
insert into ref.lnk_dose2drug (fk_drug_product, fk_dose)
	select
		pk_brand,			-- still old view
		(select pk from ref.dose r_d where
			r_d.fk_substance = (select pk from ref.substance r_s where r_s.description = r_vdc.substance)
				and
			r_d.amount = r_vdc.amount
				and
			r_d.unit = r_vdc.unit
		)
	from
		ref.v_drug_components r_vdc
;

-- --------------------------------------------------------------
drop view if exists ref.v_drug_components cascade;

create view ref.v_drug_components as
select
	r_ld2d.pk 
		as pk_component,
	r_dp.description
		as product,
	r_vsd.substance,
	r_vsd.amount,
	r_vsd.unit,
	r_vsd.dose_unit,
	r_dp.preparation
		as preparation,
	_(r_dp.preparation)
		as l10n_preparation,
	r_vsd.intake_instructions,
	r_vsd.loincs,
	r_vsd.atc_substance,
	r_dp.atc_code
		as atc_drug,
	r_dp.external_code
		as external_code,
	r_dp.external_code_type
		as external_code_type,
	r_dp.is_fake
		as is_fake_product,
	exists (
		select 1 from clin.substance_intake c_si
		where c_si.fk_drug_component = r_ld2d.pk
		limit 1
	)	as is_in_use,

	r_dp.pk
		as pk_drug_product,
	r_vsd.pk_dose,
	r_vsd.pk_substance,
	r_dp.fk_data_source
		as pk_data_source,
	r_ld2d.xmin
		as xmin_lnk_dose2drug
from
	ref.lnk_dose2drug r_ld2d
		inner join ref.drug_product r_dp on (r_ld2d.fk_drug_product = r_dp.pk)
		inner join ref.v_substance_doses r_vsd on (r_ld2d.fk_dose = r_vsd.pk_dose)
;

grant select on ref.v_drug_components to "gm-public";

-- --------------------------------------------------------------
drop function if exists ref.trf_ins_upd_assert_dose_unit_across_drug_components() cascade;

create or replace function ref.trf_ins_upd_assert_dose_unit_across_drug_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_dose_unit_count integer;
	_msg text;
BEGIN
	SELECT count(1) into strict _dose_unit_count
	FROM (
		SELECT dose_unit
		FROM ref.v_drug_components
		WHERE pk_drug_product = NEW.fk_drug_product
		GROUP BY dose_unit
	) AS dose_unit_count;

	if _dose_unit_count = 1 then
		return NEW;
	end if;

	_msg := ''[ref.trf_ins_upd_assert_dose_unit_across_drug_components()]: cannot link substance dose ['' || NEW.fk_dose || ''] ''
		|| ''to drug product ['' || NEW.fk_drug_product || ''] ''
		|| ''because all components must have the same <dose_unit>'';
	raise exception check_violation using message = _msg;

	return NEW;
END;';


comment on function ref.trf_ins_upd_assert_dose_unit_across_drug_components() is
	'Assert that all substance doses linked into a multi-component drug carry the same <dose_unit>';


create constraint trigger tr_ins_upd_assert_dose_unit_across_drug_components
	after insert or update on ref.lnk_dose2drug
	deferrable initially deferred
	for each row
	execute procedure ref.trf_ins_upd_assert_dose_unit_across_drug_components();

-- --------------------------------------------------------------
-- trigger to ensure that at the end of a tx a product still has components left
drop function if exists ref.trf_assert_product_keeps_components() cascade;

create function ref.trf_assert_product_keeps_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	PERFORM 1 FROM ref.lnk_dose2drug WHERE fk_drug_product = OLD.pk LIMIT 1;
	-- any components left ?
	IF FOUND THEN
		-- does not matter
		RETURN OLD;
	END IF;

	PERFORM 1 FROM ref.drug_product WHERE pk = OLD.fk_drug_product LIMIT 1;

	-- drug AND components deleted ?
	IF NOT FOUND THEN
		-- does not matter
		RETURN OLD;
	END IF;

	_msg := ''[ref.trf_assert_product_keeps_components()]: ''
		|| TG_OP
		|| '' failed: no components (doses) linked to drug product [''
		|| OLD.pk
		|| ''] anymore.''
	;
	RAISE EXCEPTION integrity_constraint_violation using message = _msg;

	-- does not matter
	RETURN OLD;
END;';

create constraint trigger tr_del_assert_product_keeps_components
	after
		delete
	on
		ref.lnk_dose2drug
	deferrable
		initially deferred
	for
		each row
	execute procedure
		ref.trf_assert_product_keeps_components()
;

create constraint trigger tr_upd_assert_product_keeps_components
	after
		update
	on
		ref.lnk_dose2drug
	deferrable
		initially deferred
	for
		each row
	when
		(NEW.fk_drug_product is distinct from OLD.fk_drug_product)
	execute procedure
		ref.trf_assert_product_keeps_components()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-lnk_dose2drug-dynamic.sql', '22.0');
