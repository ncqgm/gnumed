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
-- table drug_product
delete from audit.audited_tables where schema = 'ref' and table_name = 'branded_drug';
select audit.add_table_for_audit('ref', 'drug_product');

drop function if exists audit.ft_del_branded_drug() cascade;
drop function if exists audit.ft_ins_branded_drug() cascade;
drop function if exists audit.ft_upd_branded_drug() cascade;

drop trigger if exists zzz_tr_announce_ref_branded_drug_del on ref.drug_product cascade;
drop trigger if exists zzz_tr_announce_ref_branded_drug_ins_upd on ref.drug_product cascade;


delete from gm.notifying_tables where schema_name = 'ref' and table_name = 'branded_drug';
select gm.add_table_for_notifies('ref', 'drug_product');


-- table constraints
--drop index if exists ref.idx_drug_product_uniq_generic_drugs cascade;
--create unique index idx_drug_product_uniq_generic_drugs on ref.drug_product(description, preparation, is_fake);

drop index if exists ref.idx_branded_drug_uniq_brand_no_code cascade;
drop index if exists ref.idx_drug_product_uniq_product_no_code cascade;

create unique index idx_drug_product_uniq_product_no_code
	on ref.drug_product (description, preparation, is_fake)
	where ref.drug_product.external_code is NULL;


-- trigger to ensure that at the end of a tx a product does have
-- components (and, by extension, a vaccine has indications)
drop function if exists ref.trf_assert_product_has_components() cascade;

create function ref.trf_assert_product_has_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	PERFORM 1 FROM ref.lnk_dose2drug WHERE fk_drug_product = NEW.pk LIMIT 1;
	IF FOUND THEN
		RETURN NEW;
	END IF;

	_msg := ''[ref.trf_assert_product_has_components()]: ''
		|| TG_OP
		|| '' failed: no components (doses) linked to drug product [''
		|| NEW.pk
		|| ''].''
	;
	RAISE EXCEPTION integrity_constraint_violation using message = _msg;

	RETURN NEW;
END;';

create constraint trigger tr_assert_product_has_components
	after insert or update on ref.drug_product
	deferrable
	initially deferred
		for each row execute procedure ref.trf_assert_product_has_components()
;

-- --------------------------------------------------------------
-- view
drop view if exists ref.v_branded_drugs cascade;
drop view if exists ref.v_drug_products cascade;

create view ref.v_drug_products as
select
	r_dp.pk
		as pk_drug_product,
	r_dp.description
		as product,
	r_dp.preparation
		as preparation,
	_(r_dp.preparation)
		as l10n_preparation,
	r_dp.atc_code
		as atc,
	r_dp.external_code
		as external_code,
	r_dp.external_code_type
		as external_code_type,
	r_dp.is_fake
		as is_fake_product,
	exists (
		SELECT 1 FROM clin.vaccine c_v WHERE c_v.fk_drug_product = r_dp.pk
	)	as is_vaccine,
--	exists (
--		select 1 from clin.substance_intake c_si
--		where
--			c_si.fk_drug_component = r_ld2d.pk
--				and
--		limit 1
--	)	as is_in_use,
	ARRAY (
		select row_to_json(component_row) from (
			select
				r_vsd.substance,
				r_vsd.amount,
				r_vsd.unit,
				r_vsd.dose_unit,
				r_vsd.intake_instructions,
				r_vsd.loincs,
				r_vsd.atc_substance,
				r_ld2d.pk
					as pk_component,
				r_vsd.pk_dose,
				r_vsd.pk_substance
			from
				ref.lnk_dose2drug r_ld2d
					inner join ref.v_substance_doses r_vsd on (r_ld2d.fk_dose = r_vsd.pk_dose)
			where
				r_ld2d.fk_drug_product = r_dp.pk
		) as component_row
	) as components,

	r_dp.fk_data_source
		as pk_data_source,
	r_dp.xmin
		as xmin_drug_product
from
	ref.drug_product r_dp
;

grant select on ref.v_drug_products to group "gm-doctors";

-- --------------------------------------------------------------
-- only needed for data conversion
drop view if exists staging._tmp_v_drug_products cascade;

create view staging._tmp_v_drug_products as
select
	r_vdp.*,
	(select array_agg(r_vdc.pk_substance)
	 from ref.v_drug_components r_vdc
	 where r_vdc.pk_drug_product = r_vdp.pk_drug_product
	) as pk_substances
from
	ref.v_drug_products r_vdp
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-v_drug_products.sql', '22.0');
