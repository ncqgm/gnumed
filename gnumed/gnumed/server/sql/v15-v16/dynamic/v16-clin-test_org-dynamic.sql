-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.test_org drop constraint test_org_fk_org_unit_fkey cascade;
\set ON_ERROR_STOP 1


alter table clin.test_org
	add foreign key(fk_org_unit)
		references dem.org_unit(pk)
			on update cascade
			on delete restrict;


alter table clin.test_org
	alter column fk_org_unit
		set not null;


-- update Enterprise Lab
update dem.org_unit set
	fk_org = (
		select pk from dem.org where
			description = 'Starfleet Central'
	)
where
	exists (
		select pk from dem.org where description = 'Starfleet Central'
	) and
	fk_org = (
		select pk from dem.org where
			description = 'Enterprise Main Lab'
	);

\unset ON_ERROR_STOP
delete from dem.org where description = 'Enterprise Main Lab';
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_test_orgs cascade;
\set ON_ERROR_STOP 1

create or replace view clin.v_test_orgs as
select
	c_to.pk
		as pk_test_org,
	d_o.description
		as organization,
	d_ou.description
		as unit,
	c_to.comment,
	c_to.contact
		as test_org_contact,
	-- test_org keys
	c_to.fk_adm_contact
		as pk_adm_contact,
	c_to.fk_med_contact
		as pk_med_contact,
	-- dem.org keys
	d_o.pk
		as pk_org,
	d_o.fk_category
		as category_org,
	-- dem.org_unit keys
	d_ou.pk
		as pk_org_unit,
	d_ou.fk_category
		as category_unit,
	d_ou.fk_address
		as pk_address_unit,
	c_to.xmin
		as xmin_test_org
from
	clin.test_org c_to
		left join dem.org_unit d_ou on (c_to.fk_org_unit = d_ou.pk)
			left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;

grant select on clin.v_test_orgs to group "gm-public";

-- ==============================================================
select gm.log_script_insertion('v16-clin-test_org-dynamic.sql', 'v16');
