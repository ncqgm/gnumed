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
drop view if exists clin.v_intakes__active cascade;

create view clin.v_intakes__active as
select
	-- intake
	c_i.pk
		as pk_intake,
	c_i.clin_when
		as last_checked_when,
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
	case
		when c_ir.comment_on_start = '?' then null
		else c_ir.clin_when
	end::timestamp with time zone
		as started,
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
	_(r_dp.preparation)
		as l10n_preparation,
	r_dp.atc_code
		as atc_drug_product,
	r_dp.is_fake
		as is_fake_product,
	r_dp.external_code,
	r_dp.external_code_type,
	r_dp.atc_code
		as atc_drug,
	r_dp.pk
		as pk_drug_product,
	-- episode
	c_epi.description
		as episode,
	-- issue
	c_hi.description
		as health_issue,
	c_hi.pk
		as pk_health_issue,
	-- LOINCS
	ARRAY (
		select row_to_json(loinc_row) from (
			select
				r_ll2s.loinc,
				r_ll2s.comment,
				extract(epoch from r_ll2s.max_age) as max_age_in_secs,
				r_ll2s.max_age::text as max_age_str
			from ref.lnk_loinc2substance r_ll2s
			where r_ll2s.fk_substance = r_s.pk
		) as loinc_row
	)	as loincs,

	c_i.row_version,
	c_i.modified_when,
	c_i.modified_by,
	c_i.xmin
		as xmin_intake
from
	clin.intake c_i
		join ref.substance r_s on (r_s.pk = c_i.fk_substance)
		join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
		join clin.episode c_epi on (c_i.fk_episode = c_epi.pk)
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
		left join clin.intake_regimen c_ir on (c_ir.fk_intake = c_i.pk)
			left join ref.dose r_d on (r_d.pk = c_ir.fk_dose)
			left join ref.drug_product r_dp on (r_dp.pk = c_ir.fk_drug_product)

where
	c_ir.discontinued IS NULL
		OR
	c_ir.discontinued > clock_timestamp()
;


comment on view clin.v_intakes__active is
	'Which substances the patient is currently taking.';

grant select on clin.v_intakes__active to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intakes__active.sql', '23.0');
