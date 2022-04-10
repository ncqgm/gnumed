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
drop view if exists clin.v_inactive_intakes cascade;

create view clin.v_inactive_intakes as
select
	-- intake
	c_i.pk
		as pk_intake,
	c_i.clin_when
		as started_intake,
	c_i.fk_encounter
		as pk_encounter,
	c_i.fk_episode
		as pk_episode,
	c_i.narrative
		as notes4provider,
	c_i.soap_cat,
	c_i.use_type,
	c_i.fk_substance
		as pk_substance,
	c_i.notes4patient,
	-- regimen
	c_ir.pk
		as pk_intake_regimen,
	c_ir.fk_dose
		as pk_dose,
	c_ir.narrative
		as schedule,
	c_ir.clin_when
		as started_regimen,
	c_ir.comment_on_start,
	c_ir.discontinued,
	c_ir.discontinue_reason,
	c_ir.planned_duration,
	-- encounter
	c_enc.fk_patient
		as pk_patient,
	-- substance
	r_s.description
		as substance,
	r_s.atc
		as atc_substance,
	r_s.intake_instructions,
	-- dose
	r_d.amount,
	r_d.unit,
	r_d.dose_unit,
	-- product
	r_dp.description
		as drug_product,
	r_dp.preparation,
	r_dp.atc_code
		as atc_drug_product,
	r_dp.is_fake
		as is_fake_product,
	r_dp.external_code,
	r_dp.external_code_type,
	r_ld2d.pk
		as pk_drug_component
from
	clin.intake c_i
		join ref.substance r_s on (r_s.pk = c_i.fk_substance)
		left join clin.intake_regimen c_ir on (c_ir.fk_intake = c_i.pk)
			join ref.dose r_d on (r_d.pk = c_ir.fk_dose)
			left join ref.drug_product r_dp on (r_dp.pk = c_ir.fk_drug_product)
				join ref.lnk_dose2drug r_ld2d on (r_dp.pk = r_ld2d.fk_drug_product)
		join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
where
	c_ir.discontinued IS NOT NULL
;


comment on view clin.v_inactive_intakes is
	'Which substances the patient has been taking.';

grant select on clin.v_inactive_intakes to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_inactive_intakes.sql', '23.0');
