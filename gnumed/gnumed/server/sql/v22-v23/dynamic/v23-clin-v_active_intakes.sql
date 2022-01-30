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
drop view if exists clin.v_active_intakes cascade;

create view clin.v_active_intakes as
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
	c_ir.fk_drug_component
		as pk_drug_component,
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
		as pk_patient
from
	clin.intake c_i
		left join clin.intake_regimen c_ir on (c_ir.fk_intake = c_i.pk)
		join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
where
	c_ir.discontinued IS NULL
;


comment on view clin.v_active_intakes is
	'Which substances the patient is taking.';

grant select on clin.v_active_intakes to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_active_intakes.sql', '23.0');
