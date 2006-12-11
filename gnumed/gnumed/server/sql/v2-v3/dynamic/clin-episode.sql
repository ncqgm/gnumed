-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - modify clin.episode
--
-- License: GPL
-- Author: Karsten Hilbert/Syan Tan
-- 
-- ==============================================================
-- $Id: clin-episode.sql,v 1.3 2006-12-11 17:02:46 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_episode_valid_issue;
drop index clin.idx_episode_with_issue;
drop index clin.idx_episode_without_issue;
drop index clin.idx_episode_modified_by;
\set ON_ERROR_STOP 1

create index idx_episode_with_issue on clin.episode(fk_health_issue) where fk_health_issue is not null;
comment on index clin.idx_episode_with_issue is
	'index episodes with associated health issue by their issue';

create index idx_episode_without_issue on clin.episode(fk_health_issue) where fk_health_issue is null;
comment on index clin.idx_episode_without_issue is
	'index episodes without associated health issue';

create index idx_episode_modified_by on clin.episode(modified_by);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function trf_announce_episode_mod() cascade;
\set ON_ERROR_STOP 1

create function audit.trf_announce_episode_mod()
	returns trigger
	language 'plpgsql'
	as '
declare
	patient_pk integer;
begin
	-- get patient ID
	if TG_OP = ''DELETE'' then
		-- if no patient in episode
		if OLD.fk_patient is null then
			-- get it from attached health issue
			select into patient_pk fk_patient
				from clin.health_issue
				where pk = OLD.fk_health_issue;
		else
			patient_pk := OLD.fk_patient;
		end if;
	else
		-- if no patient in episode
		if NEW.fk_patient is null then
			-- get it from attached health issue
			select into patient_pk fk_patient
				from clin.health_issue
				where pk = NEW.fk_health_issue;
		else
			patient_pk := NEW.fk_patient;
		end if;
	end if;
	-- execute() the NOTIFY
	execute ''notify "episode_change_db:'' || patient_pk || ''"'';
	return NULL;
end;
';

create trigger tr_episode_mod
	after insert or delete or update
	on clin.episode
	for each row
		execute procedure audit.trf_announce_episode_mod()
;

-- --------------------------------------------------------------
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-episode.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: clin-episode.sql,v $
-- Revision 1.3  2006-12-11 17:02:46  ncq
-- - index on modified_by
--
-- Revision 1.2  2006/11/24 09:21:36  ncq
-- - fix notification trigger col name use
--
-- Revision 1.1  2006/09/25 10:55:01  ncq
-- - added here
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
