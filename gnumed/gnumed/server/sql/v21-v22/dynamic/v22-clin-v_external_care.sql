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
drop view if exists clin.v_external_care cascade;


create view clin.v_external_care as
select
	c_ec.pk
		as pk_external_care,
	(select fk_patient from clin.encounter where pk = c_ec.fk_encounter)
		as pk_identity,
	coalesce (
		c_ec.issue,
		c_hi.description
	)
		as issue,
	c_ec.provider
		as provider,
	d_ou.description
		as unit,
	d_o.description
		as organization,
	c_ec.comment
		as comment,
	c_ec.inactive
		as inactive,
	c_ec.fk_health_issue
		as pk_health_issue,
	c_ec.fk_org_unit
		as pk_org_unit,
	c_ec.fk_encounter
		as pk_encounter,
	c_ec.xmin
		as xmin_external_care,
	c_ec.modified_when,
	c_ec.modified_by,
	c_ec.row_version
from
	clin.external_care c_ec
		left join clin.health_issue c_hi on (c_hi.pk = c_ec.fk_health_issue)
			left join dem.org_unit d_ou on (c_ec.fk_org_unit = d_ou.pk)
				left join dem.org d_o on (d_ou.fk_org = d_o.pk)
;

revoke all on clin.v_external_care from public;
grant select on clin.v_external_care to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_external_care.sql', '22.0');
