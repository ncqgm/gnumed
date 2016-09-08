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
-- table constraints
drop index if exists ref.idx_branded_drug_uniq_fake cascade;
create unique index idx_branded_drug_uniq_fake on ref.branded_drug(description, is_fake);

-- --------------------------------------------------------------
drop view if exists ref.v_branded_drugs cascade;

create view ref.v_branded_drugs as
select
	r_bd.pk
		as pk_brand,
	r_bd.description
		as brand,
	r_bd.preparation
		as preparation,
	r_bd.atc_code
		as atc,
	r_bd.external_code
		as external_code,
	r_bd.external_code_type
		as external_code_type,
	r_bd.is_fake
		as is_fake_brand,
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
				r_ld2d.fk_brand = r_bd.pk
		) as component_row
	) as components,

	r_bd.fk_data_source
		as pk_data_source,
	r_bd.xmin
		as xmin_branded_drug
from
	ref.branded_drug r_bd
;

grant select on ref.v_branded_drugs to group "gm-doctors";

-- --------------------------------------------------------------
-- only needed for data conversion
drop view if exists ref._tmp_v_branded_drugs cascade;

create view ref._tmp_v_branded_drugs as
select
	r_vbd.*,
	(select array_agg(r_vdc.pk_substance)
	 from ref.v_drug_components r_vdc
	 where r_vdc.pk_brand = r_vbd.pk_brand
	) as pk_substances
from
	ref.v_branded_drugs r_vbd
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-v_branded_drugs.sql', '22.0');
