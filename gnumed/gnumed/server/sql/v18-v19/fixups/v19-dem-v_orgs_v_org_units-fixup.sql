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
-- we are only changing the join type, so no need to drop/recreate/cascade
create or replace view dem.v_orgs as
select
	d_o.pk
		as pk_org,
	d_o.description
		as organization,
	d_oc.description
		as category,
	_(d_oc.description)
		as l10n_category,
	exists (
		select 1 from dem.praxis_branch d_pb where d_pb.fk_org_unit IN (
			select d_ou.pk from dem.org_unit d_ou where d_ou.fk_org = d_o.pk
		)
	)	as is_praxis,
	d_o.fk_category
		as pk_category_org,
	d_o.xmin
		as xmin_org
from
	dem.org d_o
		left join dem.org_category d_oc on (d_o.fk_category = d_oc.pk)
;


drop view if exists dem.v_orgs_no_praxis_check cascade;

-- --------------------------------------------------------------
drop view if exists dem.v_org_units cascade;

create or replace view dem.v_org_units as
select
	d_ou.pk
		as pk_org_unit,
	d_o.description
		as organization,
	d_ou.description
		as unit,
	d_oc_o.description
		as organization_category,
	_(d_oc_o.description)
		as l10n_organization_category,
	d_oc_u.description
		as unit_category,
	_(d_oc_u.description)
		as l10n_unit_category,
	exists (select 1 from dem.praxis_branch d_pb where d_pb.fk_org_unit = d_ou.pk)
		as is_praxis_branch,
	d_o.pk
		as pk_org,
	d_o.fk_category
		as pk_category_org,
	d_ou.fk_category
		as pk_category_unit,
	d_ou.fk_address
		as pk_address,
	d_ou.xmin
		as xmin_org_unit
from
	dem.org_unit d_ou
		inner join dem.org d_o on (d_o.pk = d_ou.fk_org)
			left join dem.org_category d_oc_u on (d_ou.fk_category = d_oc_u.pk)
				left join dem.org_category d_oc_o on (d_o.fk_category = d_oc_o.pk)
;

grant select on dem.v_org_units to "gm-public";


drop view if exists dem.v_org_units_no_praxis_check cascade;

create view dem.v_org_units_no_praxis_check as
select
	d_ou.pk
		as pk_org_unit,
	d_o.description
		as organization,
	d_ou.description
		as unit,
	d_oc_o.description
		as organization_category,
	_(d_oc_o.description)
		as l10n_organization_category,
	d_oc_u.description
		as unit_category,
	_(d_oc_u.description)
		as l10n_unit_category,
	d_o.pk
		as pk_org,
	d_o.fk_category
		as pk_category_org,
	d_ou.fk_category
		as pk_category_unit,
	d_ou.fk_address
		as pk_address,
	d_ou.xmin
		as xmin_org_unit
from
	dem.org_unit d_ou
		inner join dem.org d_o on (d_o.pk = d_ou.fk_org)
			left join dem.org_category d_oc_u on (d_ou.fk_category = d_oc_u.pk)
				left join dem.org_category d_oc_o on (d_o.fk_category = d_oc_o.pk)

;

grant select on dem.v_org_units_no_praxis_check to "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-v_orgs_v_org_units-fixup.sql', '19.10');
