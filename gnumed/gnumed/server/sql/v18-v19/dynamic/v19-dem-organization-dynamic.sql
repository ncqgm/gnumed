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
\unset ON_ERROR_STOP
drop view dem.v_orgs cascade;
drop view dem.v_org_units cascade;
\set ON_ERROR_STOP 1



create view dem.v_orgs as
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



create view dem.v_org_units as

select
	d_ou.pk
		as pk_org_unit,
	d_vo.organization,
	d_ou.description
		as unit,
	d_vo.category
		as organization_category,
	_(d_vo.category)
		as l10n_organization_category,
	d_oc.description
		as unit_category,
	_(d_oc.description)
		as l10n_unit_category,
	exists (select 1 from dem.praxis_branch d_pb where d_pb.fk_org_unit = d_ou.pk)
		as is_praxis_branch,
	d_vo.pk_org,
	d_vo.pk_category_org,
	d_ou.fk_category
		as pk_category_unit,
	d_ou.fk_address
		as pk_address,
	d_ou.xmin
		as xmin_org_unit
from
	dem.org_unit d_ou
		left join dem.v_orgs d_vo on (d_ou.fk_org = d_vo.pk_org)
			left join dem.org_category d_oc on (d_ou.fk_category = d_oc.pk)
;



grant select on
	dem.v_orgs,
	dem.v_org_units
to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-organization-dynamic.sql', '19.0');
