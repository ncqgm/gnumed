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
-- $Id: clin-episode.sql,v 1.1 2007-01-04 22:58:14 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- 1) drop old consistency trigger
drop function clin.trf_ensure_episode_issue_patient_consistency() cascade;

-- 2) drop relevant constraints
alter table clin.episode
	drop constraint only_standalone_epi_has_patient;

-- 3) add fk_patient from issue to episode
update clin.episode
set fk_patient = clin.health_issue.fk_patient
from clin.health_issue
where
	clin.episode.fk_patient is NULL and
	clin.episode.fk_health_issue = clin.health_issue.pk;

-- 4) add NOT NULL constraint on fk_patient
alter table clin.episode
	alter column fk_patient
		set not null;

-- 5) add new consistency trigger
create function clin.trf_ensure_episode_issue_patient_consistency()
	returns trigger
	language 'plpgsql'
	as '
declare
	issue_patient integer;
	msg text;
begin
	-- insert or update, both have NEW.*
	if NEW.fk_health_issue is not NULL then
		select into issue_patient fk_patient from clin.health_issue where pk = NEW.fk_health_issue;
		if issue_patient != NEW.fk_patient then
			msg := ''clin.trf_ensure_episode_issue_patient_consistency(): clin.episode must have the same <fk_patient> as the clin.health_issue it is attached to'';
			raise exception ''%'', msg;
		end if;
	end if;
	return NEW;
end;';

create trigger tr_ensure_episode_issue_patient_consistency
	before insert or update on clin.episode
	for each row execute procedure clin.trf_ensure_episode_issue_patient_consistency()
;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-episode.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-episode.sql,v $
-- Revision 1.1  2007-01-04 22:58:14  ncq
-- - new
--
-- Revision 1.3  2006/11/24 09:21:50  ncq
-- - whitespace fix
--
