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
-- transfer data
insert into clin.intake_regimen (
	fk_intake,
	fk_dose,
	fk_drug_product,
	clin_when,
	comment_on_start,
	discontinued,
	discontinue_reason,
	planned_duration,
	narrative,
	fk_encounter,
	fk_episode
)
	select
		c_i.pk,
		(select pk_dose from clin.v_substance_intakes where pk_substance_intake = c_i._fk_s_i),
		(select pk_drug_product from clin.v_substance_intakes where pk_substance_intake = c_i._fk_s_i),
		c_i.clin_when,
		c_si.comment_on_start,
		c_si.discontinued,
		c_si.discontinue_reason,
		c_si.duration,
		coalesce(c_si.schedule, 'per plan'),
		c_i.fk_encounter,
		c_i.fk_episode
	from
		clin.intake c_i
			inner join clin.substance_intake c_si on (c_si.pk = c_i._fk_s_i)
	where not exists (
		select 1 from clin.intake_regimen where fk_intake = c_i.pk
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake_regimen-transfer_data.sql', '23.0');
