-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-v_most_recent_encounters.sql,v 1.1 2007-02-09 14:49:58 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_most_recent_encounters cascade;
\set ON_ERROR_STOP 1

create view clin.v_most_recent_encounters as
select
	ce1.pk as pk_encounter,
	ce1.fk_patient as pk_patient,
	ce1.reason_for_encounter as reason_for_encounter,
	ce1.assessment_of_encounter as assessment_of_encounter,
	et.description as type,
	_(et.description) as l10n_type,
	ce1.started as started,
	ce1.last_affirmed as last_affirmed,
	ce1.fk_type as pk_type,
	ce1.fk_location as pk_location
from
	clin.encounter ce1,
	clin.encounter_type et
where
	ce1.fk_type = et.pk
		and
	ce1.started = (
		-- find max of started in ...
		select max(started)
		from clin.encounter ce2
		where
			ce2.last_affirmed = (
				-- ... max of last_affirmed for patient
				select max(last_affirmed)
				from clin.encounter ce3
				where
					ce3.fk_patient = ce1.fk_patient
			)
		limit 1
	)
;


comment on view clin.v_most_recent_encounters is
	'Lists the most recent encounters per patient. Logic of "most recent" 
	is: for a patient: 
	 1) select encounters with latest "last_affirmed",
	 2) from those select encounters with latest "started"
	 3) limit those to 1 if there are duplicates (same start and end of encounter!)';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select on clin.v_most_recent_encounters to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-v_most_recent_encounters.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-v_most_recent_encounters.sql,v $
-- Revision 1.1  2007-02-09 14:49:58  ncq
-- - remove unnecessary distinct on for speed
--
--