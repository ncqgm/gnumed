-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .fk_condition_issue
comment on column clin.hx_family_item.fk_condition_issue is
	'NULL or the clin.health_issue.pk of fk_relative this relates to.';

-- --------------------------------------------------------------
-- .fk_condition_episode
comment on column clin.hx_family_item.fk_condition_episode is
	'NULL or the clin.episode.pk of fk_relative this relates to.';

-- --------------------------------------------------------------
-- table constraint on relative
\unset ON_ERROR_STOP
alter table clin.hx_family_item drop constraint link_or_know_relative cascade;
\set ON_ERROR_STOP 1


\unset ON_ERROR_STOP
alter table clin.hx_family_item drop constraint clin_hx_fam_lnk_condition_must_not_lnk_relative cascade;
\set ON_ERROR_STOP 1

alter table clin.hx_family_item
	add constraint clin_hx_fam_lnk_condition_must_not_lnk_relative check (
		((
			(fk_condition_issue is not null)
				and
			(fk_relative is null)
		))	or ((
			(fk_condition_episode is not null)
				and
			(fk_relative is null)
		))
);


\unset ON_ERROR_STOP
alter table clin.hx_family_item drop constraint clin_hx_fam_lnk_or_know_relative cascade;
\set ON_ERROR_STOP 1





-- --------------------------------------------------------------
-- table constraint on condition
\unset ON_ERROR_STOP
alter table clin.hx_family_item drop constraint link_or_know_condition cascade;
alter table clin.hx_family_item drop constraint clin_hx_fam_lnk_or_know_condition cascade;
\set ON_ERROR_STOP 1

alter table clin.hx_family_item
	add constraint clin_hx_fam_lnk_or_know_condition check (
		((
			(fk_condition_issue is not null)
				and
			(fk_condition_episode is null)
				and
			(condition is null)
		))	or ((
			(fk_condition_issue is null)
				and
			(fk_condition_episode is not null)
				and
			(condition is null)
		))	or ((
			(fk_condition_issue is null)
				and
			(fk_condition_episode is null)
				and
			(condition is not null)
		))
);




-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-hx_family_item-dynamic.sql', 'Revision: 1.1');
