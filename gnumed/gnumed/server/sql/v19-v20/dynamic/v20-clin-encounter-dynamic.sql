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
-- .fk_patient

-- populate clin.patient from clin.encounter
insert into clin.patient (fk_identity) select
	distinct on (c_e.fk_patient)
	c_e.fk_patient
from
	clin.encounter c_e
where not exists (
	select 1 from clin.patient c_p where c_p.fk_identity = c_e.fk_patient
);


-- adjust foreign key
alter table clin.encounter drop constraint if exists encounter_fk_patient_fkey cascade;
alter table clin.encounter drop constraint if exists FK_clin_encounter_fk_patient cascade;

alter table clin.encounter
	add constraint FK_clin_encounter_fk_patient foreign key (fk_patient)
		references clin.patient(fk_identity)
		on update cascade
		on delete cascade
;

-- --------------------------------------------------------------
select i18n.upd_tx('de', 'generic praxis', 'generische Praxis');
select i18n.upd_tx('de', 'generic praxis branch', 'generische Zweigstelle');

-- --------------------------------------------------------------
-- add org category to use for generic praxis if needed
insert into dem.org_category (description)
select
	'Medical Practice'
where
	not exists (
		select 1 from dem.org_category where description = 'Medical Practice'
);


-- if there is no praxis branch yet add a generic org off which
-- to base a generic org unit to use as praxis branch
insert into dem.org (description, fk_category)
select
	_('generic praxis'),
	(select pk from dem.org_category where description = 'Medical Practice')
where
	not exists (select 1 from dem.praxis_branch)
		and
	not exists (
		select 1 from dem.org
		where
			description = _('generic praxis')
				and
			fk_category = (select pk from dem.org_category where description = 'Medical Practice')
	)
;


-- if there is no praxis branch yet add a generic
-- org unit to the just created generic org
insert into dem.org_unit (fk_org, description)
select
	(select pk from dem.org where description = _('generic praxis')),
	_('generic praxis branch')
where
	not exists (select 1 from dem.praxis_branch)
		and
	not exists (
		select 1 from dem.org_unit
		where
			description = _('generic praxis branch')
				and
			fk_org = (
				select pk from dem.org where description = _('generic praxis')
			)
	)
;


-- if there is no praxis branch yet add generic one now
insert into dem.praxis_branch (fk_org_unit)
select
	pk
from
	dem.org_unit
where
	not exists (select 1 from dem.praxis_branch)
		and
	description = _('generic praxis branch')
		and
	fk_org = (
		select pk from dem.org where description = _('generic praxis')
	)
;


-- now we have got a praxis branch, either by having
-- created a generic one or because it already existed


-- add generic org unit (if it does not exist) to use
-- as praxis branch for all hitherto non-located encounters
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
select gm.log_script_insertion('v20-clin-encounter-dynamic.sql', '20.0');
