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
drop view if exists clin.v_intake_regimen cascade;

create view clin.v_intake_regimen as
select
	c_ir.pk
		as pk_intake_regimen,
	c_enc.fk_patient
		as pk_patient,
	c_ir.soap_cat,
	case
		when c_ir.start_is_unknown then null
		else c_ir.clin_when
	end::timestamp with time zone
		as started,
	c_ir.start_is_unknown,
	c_ir.comment_on_start,
	c_ir.planned_duration,
	c_ir.discontinued,
	c_ir.discontinue_reason,
	r_s.description
		as substance,
	r_s.atc
		as atc_substance,
	c_ir.amount,
	c_ir.unit,
	c_ir.narrative
		as schedule,
	c_i.use_type,
	r_s.intake_instructions,
	c_i.notes4patient,
	c_i.notes4us,
	c_i.narrative
		as notes4provider,
	c_epi.description
		as episode,
	c_ir.modified_when,
	c_ir.modified_by,
	c_i.fk_substance
		as pk_substance,
	c_ir.fk_encounter
		as pk_encounter,
	c_ir.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_ir.fk_intake
		as pk_intake,
	c_ir.row_version,
	c_ir.xmin
		as xmin_intake_regimen
from
	clin.intake_regimen c_ir
		left join clin.intake c_i on (c_ir.fk_intake = c_i.pk)
			inner join ref.substance r_s on (c_i.fk_substance = r_s.pk)
		inner join clin.encounter c_enc on (c_ir.fk_encounter = c_enc.pk)
		inner join clin.episode c_epi on c_ir.fk_episode = c_epi.pk
			left join clin.health_issue c_hi on (c_epi.fk_health_issue = c_hi.pk)
;

comment on view clin.v_intake_regimen is
	'Substance intake regimen entries.';

grant select on clin.v_intake_regimen to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intake_regimen.sql', '23.0');
