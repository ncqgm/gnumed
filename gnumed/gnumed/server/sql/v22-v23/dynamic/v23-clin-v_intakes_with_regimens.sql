-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_intakes_with_pseudo_regimens cascade;

create view clin.v_intakes_with_pseudo_regimens as
select
	-- context
	c_i.pk
		as pk_intake,
	NULL::integer
		as pk_intake_regimen,
	c_enc.fk_patient
		as pk_patient,
	-- intake
	c_i.clin_when
		as last_checked_when,
	c_i.narrative
		as notes4provider,
	c_i.soap_cat,
	c_i.use_type,
	c_i.fk_substance
		as pk_substance,
	c_i.notes4patient,
	-- regimen
	NULL::TEXT
		as schedule,
	NULL::timestamp with time zone
		as started,
	NULL::TEXT
		as comment_on_start,
	NULL::timestamp with time zone
		as discontinued,
	NULL::TEXT
		as discontinue_reason,
	NULL::INTERVAL
		as planned_duration,
	-- encounter
	c_i.fk_encounter
		as pk_encounter,
	c_i.fk_encounter
		as pk_encounter__intake,
	NULL::INTEGER
		as pk_encounter__regimen,
	-- substance
	r_s.description
		as substance,
	r_s.atc
		as atc_substance,
	r_s.intake_instructions,
	-- dose
	NULL::DECIMAL
		as amount,
	NULL::TEXT
		as unit,
	-- episode
	c_epi.description
		as episode,
	c_epi.pk
		as pk_episode,
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

	c_i.row_version
		as row_version__intake,
	c_i.modified_when
		as modified_when__intake,
	c_i.modified_by
		as modified_by__intake,
	c_i.xmin
		as xmin_intake,
	NULL::INTEGER
		as row_version__regimen,
	NULL::timestamp with time zone
		as modified_when__regimen,
	NULL::TEXT
		as modified_by__regimen,
	NULL::XID
		as xmin_regimen
from
	clin.intake c_i
		join ref.substance r_s on (r_s.pk = c_i.fk_substance)
		join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
		join clin.episode c_epi on (c_i.fk_episode = c_epi.pk)
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
where
	c_i.pk not in (select fk_intake from clin.intake_regimen)
;

comment on view clin.v_intakes_with_pseudo_regimens is
'Substance intakes without any regimens, with pseudo regimen added to each.';

grant select on clin.v_intakes_with_pseudo_regimens to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_intakes_with_real_regimens cascade;

create view clin.v_intakes_with_real_regimens as
select
	-- context
	c_i.pk
		as pk_intake,
	c_ir.pk
		as pk_intake_regimen,
	c_enc.fk_patient
		as pk_patient,
	-- intake
	c_i.clin_when
		as last_checked_when,
	c_i.narrative
		as notes4provider,
	c_i.soap_cat,
	c_i.use_type,
	c_i.fk_substance
		as pk_substance,
	c_i.notes4patient,
	-- regimen
	c_ir.narrative
		as schedule,
	case
		when c_ir.comment_on_start = '?' then null
		else coalesce(c_ir.clin_when, c_i.clin_when)
	end::timestamp with time zone
		as started,
	c_ir.comment_on_start,
	c_ir.discontinued,
	c_ir.discontinue_reason,
	c_ir.planned_duration,
	-- encounter
	coalesce(c_ir.fk_encounter, c_i.fk_encounter)
		as pk_encounter,
	c_i.fk_encounter
		as pk_encounter__intake,
	c_ir.fk_encounter
		as pk_encounter__regimen,
	-- substance
	r_s.description
		as substance,
	r_s.atc
		as atc_substance,
	r_s.intake_instructions,
	-- dose
	c_ir.amount,
	c_ir.unit,
	-- episode
	coalesce(c_epi__r.description, c_epi__i.description)
		as episode,
	coalesce(c_epi__r.pk, c_epi__i.pk)
		as pk_episode,
	-- issue
	coalesce(c_hi__r.description, c_hi__i.description)
		as health_issue,
	coalesce(c_hi__r.pk, c_hi__i.pk)
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

	c_i.row_version
		as row_version__intake,
	c_i.modified_when
		as modified_when__intake,
	c_i.modified_by
		as modified_by__intake,
	c_i.xmin
		as xmin_intake,
	c_ir.row_version
		as row_version__regimen,
	c_ir.modified_when
		as modified_when__regimen,
	c_ir.modified_by
		as modified_by__regimen,
	c_ir.xmin
		as xmin_regimen
from
	clin.intake c_i
		join ref.substance r_s on (r_s.pk = c_i.fk_substance)
		join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
		join clin.episode c_epi__i on (c_i.fk_episode = c_epi__i.pk)
			left join clin.health_issue c_hi__i on (c_epi__i.fk_health_issue = c_hi__i.pk)
		left join clin.intake_regimen c_ir on (c_ir.fk_intake = c_i.pk)
			join clin.episode c_epi__r on (c_ir.fk_episode = c_epi__r.pk)
				left join clin.health_issue c_hi__r on (c_epi__r.fk_health_issue = c_hi__r.pk)
;

comment on view clin.v_intakes_with_real_regimens is
'Substance intakes with real regimens, one row per regimen, thus, denormalized intakes.';

grant select on clin.v_intakes_with_real_regimens to group "gm-doctors";

-- --------------------------------------------------------------
drop view if exists clin.v_intakes_with_regimens cascade;

create view clin.v_intakes_with_regimens as
	SELECT * FROM clin.v_intakes_with_pseudo_regimens

		UNION ALL

	SELECT * FROM clin.v_intakes_with_real_regimens
;

comment on view clin.v_intakes_with_regimens is
'Substance intake with regimens.
.
- one row per regimen, thus, denormalized intakes
- one row per intake-without-any-regimen, with pseudo-regimen
';

grant select on clin.v_intakes_with_regimens to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intakes_with_regimens.sql', '23.0');
