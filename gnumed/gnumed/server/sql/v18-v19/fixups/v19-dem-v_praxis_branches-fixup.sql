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
	d_pb.pk
		as pk_praxis_branch,
	d_vou.organization
		as praxis,
	d_vou.unit
		as branch,
	d_vou.organization_category,
	d_vou.l10n_organization_category,
	d_vou.unit_category,
	d_vou.l10n_unit_category,
	d_vou.pk_org,
	d_pb.fk_org_unit
		as pk_org_unit,
	d_vou.pk_category_org,
	d_vou.pk_category_unit,
	d_vou.pk_address,
	d_pb.xmin
		as xmin_praxis_branch,
	d_vou.xmin_org_unit
from
	dem.praxis_branch d_pb
		inner join dem.v_org_units_no_praxis_check d_vou on (d_pb.fk_org_unit = d_vou.pk_org_unit)
;


comment on view dem.v_praxis_branches is 'Denormalized praxis branches with their praxis.';


grant select on dem.v_praxis_branches to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-v_praxis_branches-fixup.sql', '19.9');
