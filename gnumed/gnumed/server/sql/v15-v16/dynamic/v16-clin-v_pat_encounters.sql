-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_encounters cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_encounters as
select
	c_enc.pk as pk_encounter,
	c_enc.fk_patient as pk_patient,
	c_enc.started as started,
	et.description as type,
	_(et.description) as l10n_type,
	c_enc.reason_for_encounter as reason_for_encounter,
	c_enc.assessment_of_encounter as assessment_of_encounter,
	c_enc.last_affirmed as last_affirmed,
	c_enc.source_time_zone,
	(select started at time zone (
		select source_time_zone
		from clin.encounter c_enc1
		where c_enc1.pk = c_enc.pk
	)) as started_original_tz,
	(select last_affirmed at time zone (
		select source_time_zone
		from clin.encounter c_enc1
		where c_enc1.pk = c_enc.pk
	)) as last_affirmed_original_tz,
	c_enc.fk_location as pk_location,
	c_enc.fk_type as pk_type,
	coalesce (
		(select array_agg(c_lc2r.fk_generic_code) from clin.lnk_code2rfe c_lc2r where c_lc2r.fk_item = c_enc.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes_rfe,
	coalesce (
		(select array_agg(c_lc2a.fk_generic_code) from clin.lnk_code2aoe c_lc2a where c_lc2a.fk_item = c_enc.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes_aoe,
	c_enc.xmin as xmin_encounter
from
	clin.encounter c_enc,
	clin.encounter_type et
where
	c_enc.fk_type = et.pk
;


comment on view clin.v_pat_encounters is
	'Details on encounters.';


-- views
grant select on clin.v_pat_encounters TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_pat_encounters.sql', 'v16');

-- ==============================================================
