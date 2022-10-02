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
drop view if exists clin.v_intakes cascade;

create view clin.v_intakes as
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
	-- encounter
	c_enc.fk_patient
		as pk_patient,
	-- substance
	r_s.description
		as substance,
	r_s.atc
		as atc_substance,
	r_s.intake_instructions,
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
;

comment on view clin.v_intakes is
	'Substance intakes, without regimens.';

grant select on clin.v_intakes to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intakes.sql', '23.0');
