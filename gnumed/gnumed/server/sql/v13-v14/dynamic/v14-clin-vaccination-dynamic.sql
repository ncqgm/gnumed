-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .narrative
comment on column clin.vaccination.narrative is
	'Used to record a comment on this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_narrative cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_narrative check (
		gm.is_null_or_non_empty_string(narrative) is true
	);


-- .reaction
comment on column clin.vaccination.reaction is
	'Used to record reactions to this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_reaction cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_reaction check (
		gm.is_null_or_non_empty_string(reaction) is true
	);


-- .site
comment on column clin.vaccination.site is
	'The site of injection used in this vaccination.';

\unset ON_ERROR_STOP
alter table clin.vaccination drop constraint vaccination_sane_site cascade;
\set ON_ERROR_STOP 1

alter table clin.vaccination
	add constraint vaccination_sane_site check (
		gm.is_null_or_non_empty_string(site) is true
	);

alter table clin.vaccination
	alter column site
		set default null;

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-vaccination-dynamic.sql', 'Revision: 1.1');
