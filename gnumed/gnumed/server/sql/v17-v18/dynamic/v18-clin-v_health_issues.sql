-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_health_issues cascade;
\set ON_ERROR_STOP 1


create view clin.v_health_issues as
select
	(select fk_patient from clin.encounter where pk = c_hi.fk_encounter)
		as pk_patient,
	c_hi.pk as pk_health_issue,
	c_hi.description,
	c_hi.summary,
	c_hi.laterality,
	c_hi.age_noted,
	c_hi.is_active,
	c_hi.clinically_relevant,
	c_hi.is_confidential,
	c_hi.is_cause_of_death,
	c_hi.fk_encounter as pk_encounter,
	c_hi.modified_when,
	c_hi.modified_by,
	c_hi.row_version,
	c_hi.grouping,
	c_hi.diagnostic_certainty_classification,
	exists (
		select 1 from clin.episode c_ep where fk_health_issue = c_hi.pk and c_ep.is_open is True limit 1
	) as has_open_episode,
	coalesce (
		(select array_agg(c_lc2h.fk_generic_code) from clin.lnk_code2h_issue c_lc2h where c_lc2h.fk_item = c_hi.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes,
	c_hi.xmin as xmin_health_issue
from
	clin.health_issue c_hi
;


grant select on clin.v_health_issues TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v18-clin-v_health_issues.sql', '18.0');
