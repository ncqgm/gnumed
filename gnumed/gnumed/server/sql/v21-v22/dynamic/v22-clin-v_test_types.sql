-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop index if exists clin.idx_test_type_loinc cascade;
create index idx_test_type_loinc on clin.test_type(loinc) where (loinc is not null);

-- --------------------------------------------------------------
drop view if exists clin.v_test_types cascade;


create view clin.v_test_types as
select
	-- original test type
	c_tt.pk
		as pk_test_type,
	c_tt.abbrev,
	c_tt.name,
	c_tt.loinc,
	c_tt.reference_unit,
	c_tt.comment
		as comment_type,

	-- lab
	d_ou.description
		as name_org,
	c_to.comment
		as comment_org,
	c_to.contact
		as contact_org,

	-- unified test_type
	coalesce(c_mtt.abbrev, c_tt.abbrev) as unified_abbrev,
	coalesce(c_mtt.name, c_tt.name) as unified_name,
	coalesce(c_mtt.loinc, c_tt.loinc) as unified_loinc,

	-- meta test_type
	(c_tt.fk_meta_test_type is null) as is_fake_meta_type,
	c_mtt.abbrev as abbrev_meta,
	c_mtt.name as name_meta,
	c_mtt.loinc as loinc_meta,
	c_mtt.comment as comment_meta,

	-- panels
	(select array_agg(pk_test_panel) from clin.v_test_types4test_panel c_vtt4tp where c_vtt4tp.pk_test_type = c_tt.pk)
		as pk_test_panels,

	-- admin links
	c_tt.fk_test_org
		 as pk_test_org,
	c_tt.fk_meta_test_type
		as pk_meta_test_type,
	c_to.fk_org_unit
		as pk_org_unit,
	c_to.fk_adm_contact
		as pk_adm_contact_org,
	c_to.fk_med_contact
		as pk_med_contact_org,
	c_tt.xmin
		as xmin_test_type
from
	clin.test_type c_tt
		left join clin.test_org c_to on (c_to.pk = c_tt.fk_test_org)
			left join dem.org_unit d_ou on (c_to.fk_org_unit = d_ou.pk)
				left outer join clin.meta_test_type c_mtt on (c_tt.fk_meta_test_type = c_mtt.pk)
;


comment on view clin.v_test_types is
'denormalizes test types with test orgs and meta types';


grant select on clin.v_test_types to group "gm-doctors";

-- ==============================================================
select gm.log_script_insertion('v22-clin-v_test_types.sql', '22.0');
