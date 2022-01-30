-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- recreate views
drop view if exists clin.v_intakes cascade;

create view clin.v_intakes as
select
	c_i.pk
		as pk_intake,
	c_enc.fk_patient
		as pk_patient,
	c_i.fk_drug
		as pk_drug,
	c_i.clin_when
		as clin_when,
	c_i.use_type,
	c_i.soap_cat,
	coalesce(r_dp.description, c_i.narrative)
		product,
	r_dp.preparation,
	_(r_dp.preparation)
		as l10n_preparation,
	c_i.notes4patient,
	c_i.notes4provider,
	r_dp.atc_code
		as atc_drug,
	r_dp.external_code
		as external_code_product,
	r_dp.external_code_type
		as external_code_type_product,
	r_dp.is_fake
		as is_fake_product,
	c_i.fk_encounter
		as pk_encounter,
	c_i.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_i.modified_when,
	c_i.modified_by
		as modified_by,
	c_i.row_version
		as row_version,
	c_i.xmin
		as xmin_intake
from
	clin.intake c_i
		left join clin.encounter c_enc on (c_enc.pk = c_i.fk_encounter)
		left join clin.episode c_epi on (c_epi.pk = c_i.fk_episode)
			left join clin.health_issue c_hi on (c_hi.pk = c_epi.fk_health_issue)
		inner join ref.drug_product r_dp on (c_i.fk_drug = r_dp.pk)
;

-- --------------------------------------------------------------
drop view if exists clin.v_substance_intakes cascade;

create view clin.v_substance_intakes as
select
	-- coalesced view
	c_i.pk
		as pk_intake,
	c_ir.pk
		as pk_intake_regimen,
	coalesce(c_enc_ir.fk_patient, c_enc_i.fk_patient)
		as pk_patient,

	c_i.soap_cat,
	r_dp.description
		as product,
	r_dp.preparation,
	_(r_dp.preparation)
		as l10n_preparation,
	r_s.description
		as substance,
	r_d.amount,
	r_d.unit,
	r_d.dose_unit,
	case
		when c_ir.comment_on_start = '?' then null
		else coalesce(c_ir.clin_when, c_i.clin_when)
	end::timestamp with time zone
		as started,
	c_ir.comment_on_start,
	c_ir.narrative
		AS schedule,
	c_ir.planned_duration,
	c_ir.discontinued,
	c_ir.discontinue_reason,

	c_i.narrative
		as notes,
	c_i.notes4patient,
	c_i.notes4provider,
	r_s.intake_instructions,
	c_i.use_type,
	coalesce(c_epi_ir.description, c_epi_i.description)
		as episode,
	coalesce(c_hi_ir.description, c_hi_i.description)
		as health_issue,

	r_s.atc
		as atc_substance,
	r_dp.atc_code
		as atc_drug,
	r_dp.external_code
		as external_code_product,
	r_dp.external_code_type
		as external_code_type_product,
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

	r_dp.is_fake
		as is_fake_product,

	r_ld2d.fk_drug_product
		as pk_drug_product,
	r_dp.fk_data_source
		as pk_data_source,
	r_ld2d.fk_dose
		as pk_dose,
	r_ld2d.pk
		as pk_drug_component,
	r_d.fk_substance
		as pk_substance,

	-- denormalized
	c_i.fk_encounter
		as pk_encounter__intake,
	c_ir.fk_encounter
		as pk_encounter__regimen,

	c_i.fk_episode
		as pk_episode__intake,
	c_ir.fk_episode
		as pk_episode__regimen,

	c_epi_i.fk_health_issue
		as pk_health_issue__intake,
	c_epi_ir.fk_health_issue
		as pk_health_issue__regimen,

	c_i.clin_when
		as clin_when__intake,
	c_ir.clin_when
		as clin_when__regimen,

	c_i.modified_when,
	c_i.modified_by
		as modified_by,
	c_i.row_version
		as row_version,
	c_i.xmin
		as xmin_intake
from
	clin.intake c_i
		-- pull in encounter/episode/issue details for intake
		left join clin.encounter c_enc_i on (c_i.fk_encounter = c_enc_i.pk)
		left join clin.episode c_epi_i on (c_i.fk_episode = c_epi_i.pk)
			left join clin.health_issue c_hi_i on (c_hi_i.pk = c_epi_i.fk_health_issue)
		-- pull in regimen
		left join clin.intake_regimen c_ir on (c_ir.fk_intake = c_i.pk)
			-- pull in encounter/episode/issue details for regimen
			left join clin.encounter c_enc_ir on (c_ir.fk_encounter = c_enc_ir.pk)
			left join clin.episode c_epi_ir on (c_ir.fk_episode = c_epi_ir.pk)
				left join clin.health_issue c_hi_ir on (c_hi_ir.pk = c_epi_ir.fk_health_issue)
		-- pull in substance details, generating one row per substance
		inner join ref.drug_product r_dp on (c_i.fk_drug = r_dp.pk)
			inner join ref.lnk_dose2drug r_ld2d on (r_ld2d.fk_drug_product = r_dp.pk)
				inner join ref.dose r_d on (r_d.pk = r_ld2d.fk_dose)
					inner join ref.substance r_s on (r_s.pk = r_d.fk_substance)
;

comment on view clin.v_substance_intakes is
	'Which substances the patient is/has ever been taking.';

grant select on clin.v_substance_intakes to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intakes.sql', '23.0');
