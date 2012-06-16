-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v12-clin-v_health_issues.sql,v 1.1 2009-09-01 22:12:47 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_health_issues cascade;
\set ON_ERROR_STOP 1


create view clin.v_health_issues as
select
	(select fk_patient from clin.encounter where pk = chi.fk_encounter)
		as pk_patient,
	chi.pk as pk_health_issue,
	chi.description,
	chi.laterality,
	chi.age_noted,
	chi.is_active,
	chi.clinically_relevant,
	chi.is_confidential,
	chi.is_cause_of_death,
	chi.fk_encounter as pk_encounter,
	chi.modified_when,
	chi.modified_by,
	chi.row_version,
	chi.grouping,
	chi.diagnostic_certainty_classification,
	chi.xmin as xmin_health_issue
from
	clin.health_issue chi
;


grant select on clin.v_health_issues TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-v_health_issues.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-clin-v_health_issues.sql,v $
-- Revision 1.1  2009-09-01 22:12:47  ncq
-- - new
--
--