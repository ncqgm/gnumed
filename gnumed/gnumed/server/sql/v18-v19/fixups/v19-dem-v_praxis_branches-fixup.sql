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
drop view if exists dem.v_praxis_branches cascade;

create view dem.v_praxis_branches as

select
	branches_w_orgs.*,
	d_ocat.description
		as organization_category,
	_(d_ocat.description)
		as l10n_organization_category,
	d_ucat.description
		as unit_category,
	_(d_ucat.description)
		as l10n_unit_category
from (
	select
		branches_w_units.*,
		d_o.description
				as praxis,
		d_o.fk_category
			as pk_category_org
	from (
		select
			d_pb.pk
				as pk_praxis_branch,
			d_ou.description
				as branch,
			d_pb.fk_org_unit
				as pk_org_unit,
			d_ou.fk_category
				as pk_category_unit,
			d_ou.fk_address
				as pk_address,
			d_ou.fk_org
				as pk_org,
			d_pb.xmin
				as xmin_praxis_branch,
			d_ou.xmin
				as xmin_org_unit
		from
			dem.praxis_branch d_pb
				inner join dem.org_unit d_ou on (d_pb.fk_org_unit = d_ou.pk)
		) as branches_w_units
			inner join dem.org d_o on (d_o.pk = branches_w_units.pk_org)
	) as branches_w_orgs
		-- LEFT JOIN needed because org/unit might lack a category
		left join dem.org_category d_ucat on (branches_w_orgs.pk_category_unit = d_ucat.pk)
			left join dem.org_category d_ocat on (branches_w_orgs.pk_category_org = d_ocat.pk)
;


comment on view dem.v_praxis_branches is 'Denormalized praxis branches with their praxis.';


grant select on dem.v_praxis_branches to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-v_praxis_branches-fixup.sql', '19.9');
