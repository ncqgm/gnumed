-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table dem.org
	add column fk_data_source integer;

alter table audit.log_org
	add column fk_data_source integer;

-- --------------------------------------------------------------
-- create orgs from test_org
insert into dem.org (
	description,
	fk_category
) select distinct on (c_to.internal_name)
	c_to.internal_name,
	(select pk from dem.org_category where dem.org_category.description = 'Laboratory')
 from
 	clin.test_org c_to
 where not exists (
	select 1 from dem.org d_o where
		d_o.description = c_to.internal_name
			and
		d_o.fk_category = (select pk from dem.org_category d_oc where d_oc.description = 'Laboratory')
	limit 1
 	)
;


-- create org_units from test_org
insert into dem.org_unit (
	description,
	fk_org,
	fk_category
) select distinct on (clin.test_org.internal_name)
	clin.test_org.internal_name,
	(select pk from dem.org where
		dem.org.description = clin.test_org.internal_name
			and
		dem.org.fk_category = (
			select pk from dem.org_category where dem.org_category.description = 'Laboratory'
		)
	),
	(select pk from dem.org_category where dem.org_category.description = 'Laboratory')
 from
 	clin.test_org
 where not exists (
	select 1 from dem.org_unit where
		dem.org_unit.description = clin.test_org.internal_name
			and
		dem.org_unit.fk_org = (
			select pk from dem.org where
				dem.org.description = clin.test_org.internal_name
					and
				dem.org.fk_category = (
					select pk from dem.org_category where dem.org_category.description = 'Laboratory'
				)
		)
	limit 1
 	)
;


-- adjust foreign key
update clin.test_org set
	fk_org = (
		select pk from dem.org_unit where
			dem.org_unit.description = clin.test_org.internal_name
				and
			dem.org_unit.fk_category = (select pk from dem.org_category where dem.org_category.description = 'Laboratory')
	);

alter table clin.test_org
	rename column fk_org to fk_org_unit;

alter table audit.log_test_org
	rename column fk_org to fk_org_unit;


-- drop unneeded columns
alter table clin.test_org
	drop column internal_name cascade;

alter table audit.log_test_org
	drop column internal_name cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-test_org-static.sql', '16.0');
