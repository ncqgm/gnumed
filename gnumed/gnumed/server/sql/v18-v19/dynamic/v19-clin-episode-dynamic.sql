-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

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
select gm.log_script_insertion('v19-clin-episode-dynamic.sql', '19.0');
