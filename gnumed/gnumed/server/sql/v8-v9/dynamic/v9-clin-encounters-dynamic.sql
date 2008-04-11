-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-encounters-dynamic.sql,v 1.1 2008-04-11 12:18:37 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_encounters cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_encounters as
select
	cle.pk as pk_encounter,
	cle.fk_patient as pk_patient,
	cle.started as started,
	et.description as type,
	_(et.description) as l10n_type,
	cle.reason_for_encounter as reason_for_encounter,
	cle.assessment_of_encounter as assessment_of_encounter,
	cle.last_affirmed as last_affirmed,
	cle.source_time_zone,
	(select started at time zone (
		select source_time_zone
		from clin.encounter cle1
		where cle1.pk = cle.pk
	)) as started_original_tz,
	(select last_affirmed at time zone (
		select source_time_zone
		from clin.encounter cle1
		where cle1.pk = cle.pk
	)) as last_affirmed_original_tz,
	cle.fk_location as pk_location,
	cle.fk_type as pk_type,
	cle.xmin as xmin_encounter
from
	clin.encounter cle,
	clin.encounter_type et
where
	cle.fk_type = et.pk
;


comment on view clin.v_pat_encounters is
	'Details on encounters.';


-- views
grant select on
	clin.v_pat_encounters
TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-encounters-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-encounters-dynamic.sql,v $
-- Revision 1.1  2008-04-11 12:18:37  ncq
-- - new file
--
--
