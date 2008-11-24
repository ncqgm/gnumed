-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-episode-dynamic.sql,v 1.1 2008-11-24 11:05:32 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop function clin.trf_ensure_episode_issue_patient_consistency() cascade;


create function clin.trf_ensure_episode_issue_patient_consistency()
	returns trigger
	language 'plpgsql'
	as '
declare
	issue_patient integer;
	msg text;
begin
	-- insert or update, both have NEW.*

	if NEW.fk_health_issue is NULL then
		return NEW;
	end if;

	select into issue_patient fk_patient from clin.encounter where pk = (
		select fk_encounter from clin.health_issue where pk = NEW.fk_health_issue
	);
	if issue_patient != NEW.fk_patient then
		msg := ''clin.trf_ensure_episode_issue_patient_consistency(): clin.episode must have the same <fk_patient> as the clin.health_issue it is attached to'';
		raise exception ''%'', msg;
	end if;

	return NEW;
end;';


create trigger tr_ensure_episode_issue_patient_consistency
	before insert or update on clin.episode
	for each row execute procedure clin.trf_ensure_episode_issue_patient_consistency()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-episode-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-episode-dynamic.sql,v $
-- Revision 1.1  2008-11-24 11:05:32  ncq
-- - fix patient consistency trigger
--
--