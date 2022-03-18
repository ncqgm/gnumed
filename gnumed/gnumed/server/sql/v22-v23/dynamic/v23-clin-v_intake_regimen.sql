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
-- start of intake regimen
drop view if exists clin.v_intake_regimen cascade;

create view clin.v_intake_regimen as
select
	c_ir.pk
		as pk_intake_regimen,
	c_enc.fk_patient
		as pk_patient,
	c_ir.soap_cat,
	c_ir.clin_when
		as started,
	c_ir.comment_on_start,
	c_ir.planned_duration,
	c_ir.discontinued,
	c_ir.discontinue_reason,
	r_s.description
		as substance,
	r_s.atc
		as atc_substance,
	r_d.amount,
	r_d.unit,
	r_d.dose_unit,
	r_dp.description
		as product,
	r_dp.preparation,
	r_dp.atc_code
		as atc_product,
	r_dp.external_code_type,
	r_dp.external_code,
	c_i.use_type,
	r_s.intake_instructions,
	c_i.notes4patient,
	c_i.narrative
		as notes4provider,
	c_ir.modified_when,
	c_ir.modified_by,
	c_ir.fk_encounter
		as pk_encounter,
	c_ir.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_i.pk
		as pk_intake,
	c_ir.row_version
from
	clin.intake_regimen c_ir
		inner join clin.intake c_i on (c_ir.fk_intake = c_i.pk)
			inner join ref.substance r_s on (c_i.fk_substance = r_s.pk)
		inner join clin.encounter c_enc on (c_ir.fk_encounter = c_enc.pk)
		inner join clin.episode c_epi on c_ir.fk_episode = c_epi.pk
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
		left join ref.dose r_d on (c_ir.fk_dose = r_d.pk)
		left join ref.lnk_dose2drug r_ld2d on (c_ir.fk_drug_component = r_ld2d.pk)
			inner join ref.drug_product r_dp on (r_ld2d.fk_drug_product = r_dp.pk)
;

comment on view clin.v_intake_regimen is
	'Substance intake regimen entries.';

grant select on clin.v_intake_regimen to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intake_regimen.sql', '23.0');
