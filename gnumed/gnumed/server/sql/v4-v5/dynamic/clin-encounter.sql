-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: 
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- adjust data
-- never worked because it lacks an ")"
--update clin.encounter
--	set last_affirmed = (started + '1 second'::interval
--where
--	started > last_affirmed;
--;


-- commented out because it never worked due to a missing ")" above
--alter table clin.encounter
--	add constraint encounter_must_start_before_it_ends
--		check (started <= last_affirmed);

--comment on forgot_to_edit_comment is
--	'';

-- --------------------------------------------------------------
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-encounter.sql,v $', '$Revision: 1.2 $');
