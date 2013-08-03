-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;

-- --------------------------------------------------------------
alter table clin.health_issue drop constraint if exists episode_sane_summary cascade;

update clin.episode set
	summary = gm.nullify_empty_string(summary);

alter table clin.episode drop constraint if exists episode_sane_summary cascade;

alter table clin.episode
	add constraint episode_sane_summary check (
		gm.is_null_or_non_empty_string(summary)
	)
;

-- --------------------------------------------------------------
drop function if exists clin.trf_activate_issue_on_opening_episode() cascade;

create function clin.trf_activate_issue_on_opening_episode()
	returns trigger
	language 'plpgsql'
	as '
begin
	if TG_OP = ''UPDATE'' then
		if OLD.is_open is TRUE then
			return NEW;
		end if;
	end if;

	update clin.health_issue
	set is_active = TRUE
	where
		pk = NEW.fk_health_issue
			AND
		is_active is FALSE
	;
	return NEW;
end;';

create trigger tr_activate_issue_on_opening_episode
	after insert or update on clin.episode
	for each row when (
		NEW.fk_health_issue is not NULL
			AND
		NEW.is_open is TRUE
	)
	execute procedure clin.trf_activate_issue_on_opening_episode()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-episode-dynamic.sql', '19.0');
