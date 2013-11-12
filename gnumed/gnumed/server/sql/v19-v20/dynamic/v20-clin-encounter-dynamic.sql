-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- add generic branch to use for all hitherto non-located encounters
insert into dem.org_unit (fk_org, description)
select
	(select fk_org from dem.org_unit where pk = (
		select fk_org_unit from dem.praxis_branch limit 1
	)),
	_('generic praxis branch')
where not exists (
	select 1 from dem.org_unit
	where
		description = _('generic praxis branch')
			and
		fk_org = (
			select fk_org from dem.org_unit where pk = (
				select fk_org_unit from dem.praxis_branch limit 1
			)
		)
);


-- set heretofore un-located encounters to generic praxis branch
update clin.encounter set
	fk_location = (
		select pk from dem.org_unit
		where
			description = _('generic praxis branch')
				and
			fk_org = (
				select fk_org from dem.org_unit where pk = (
					select fk_org_unit from dem.praxis_branch limit 1
				)
			)
	)
where
	fk_location is null
;


-- add not-NULL constraint
alter table clin.encounter
	alter column fk_location
		set not null;

-- --------------------------------------------------------------
select i18n.upd_tx('de', 'generic praxis branch', 'generische Zweigstelle');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-encounter-dynamic.sql', '20.0');
