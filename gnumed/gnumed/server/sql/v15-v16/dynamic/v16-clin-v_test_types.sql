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
drop view clin.v_test_types cascade;
\set ON_ERROR_STOP 1

create view clin.v_test_types as
select
	ctt.pk
		 as pk_test_type,
	ctt.abbrev,
	ctt.name,
	ctt.loinc,
	ctt.code,
	ctt.coding_system,
	ctt.conversion_unit,
	ctt.comment
		as comment_type,
	d_ou.description
		as name_org,
	cto.comment
		as comment_org,
	cto.contact
		as contact_org,
	-- admin links
	ctt.fk_test_org
		 as pk_test_org,
	cto.fk_org_unit
		as pk_org_unit,
	cto.fk_adm_contact
		as pk_adm_contact_org,
	cto.fk_med_contact
		as pk_med_contact_org,
	ctt.xmin
		as xmin_test_type
from
	clin.test_type ctt
		left join clin.test_org cto on (cto.pk = ctt.fk_test_org)
			left join dem.org_unit d_ou on (cto.fk_org_unit = d_ou.pk)
;


comment on view clin.v_test_types is
'denormalizes test types with test orgs';


grant select on clin.v_test_types to group "gm-doctors";

-- ==============================================================
select gm.log_script_insertion('v16-clin-v_test_types.sql', 'v16');
