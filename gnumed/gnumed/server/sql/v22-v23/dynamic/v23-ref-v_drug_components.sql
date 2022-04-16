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
select gm.log_script_insertion('v23-ref-v_drug_components.sql', '23.0');
