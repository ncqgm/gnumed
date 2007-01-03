-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: clin-encounter.sql,v 1.2 2007-01-03 11:57:33 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_encounter_modified_by;
\set ON_ERROR_STOP 1

create index idx_encounter_modified_by on clin.encounter(modified_by);


\unset ON_ERROR_STOP
drop function clin.trf_ensure_episode_issue_patient_consistency() cascade;
\set ON_ERROR_STOP 1

create function clin.trf_ensure_episode_issue_patient_consistency()
	returns trigger
	language 'plpgsql'
	as '
declare
	issue_patient integer;
	msg text;
begin
	if NEW.fk_health_issue is not NULL then
		if NEW.fk_patient is not NULL then
			select into issue_patient fk_patient from clin.health_issue where pk = NEW.fk_health_issue;
			if issue_patient = NEW.fk_patient then
				NEW.fk_patient := NULL;
			end if;
		end if;
	end if;
	-- if unlinking from health issue: carry over patient
	if TG_OP = ''UPDATE'' then
		if (NEW.fk_health_issue is NULL) and (OLD.fk_health_issue is not NULL) then
			select into issue_patient fk_patient from clin.health_issue where pk = OLD.fk_health_issue;
			if NEW.fk_patient is NULL then
				NEW.fk_patient := issue_patient;
			else
				-- do not change patient and unlink from issue at the same time ...
				if NEW.fk_patient != issue_patient then
					msg := ''trf_ensure_episode_issue_patient_consistency(): unlinking from health issue and changing patient at the same time is not allowed'';
					raise exception ''%'', msg;
				end if;
			end if;
		end if;
	end if;
	return NEW;
end;';

create trigger tr_ensure_episode_issue_patient_consistency
	before insert or update on clin.episode
	for each row execute procedure clin.trf_ensure_episode_issue_patient_consistency()
;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-encounter.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-encounter.sql,v $
-- Revision 1.2  2007-01-03 11:57:33  ncq
-- - clin.health_issue has fk_patient, not pk_patient, so use that in trigger
--
-- Revision 1.1  2006/12/11 16:59:47  ncq
-- - use dem.v_staff -> dem.staff in provider resolution
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
