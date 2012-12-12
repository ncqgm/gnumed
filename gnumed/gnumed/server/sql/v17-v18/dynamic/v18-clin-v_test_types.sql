-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .fk_test_org
\unset ON_ERROR_STOP
drop index clin.test_type_fk_test_org_idx cascade;
drop index clin.idx_test_type_fk_test_org cascade;
\set ON_ERROR_STOP 1

create index idx_test_type_fk_test_org on clin.test_type(fk_test_org);

-- --------------------------------------------------------------
-- .fk_meta_test_type
comment on column clin.test_type.fk_meta_test_type is
	'Link to the meta test type (if any) this test type is to be aggregated under.';


\unset ON_ERROR_STOP
drop index clin.test_type_fk_meta_test_type_idx cascade;
drop index idx_test_type_fk_meta_test_type cascade;
alter table clin.test_type drop constraint test_type_fk_meta_test_type_fkey cascade;
\set ON_ERROR_STOP 1

create index idx_test_type_fk_meta_test_type on clin.test_type(fk_meta_test_type);

alter table clin.test_type
	add foreign key (fk_meta_test_type)
		references clin.meta_test_type(pk);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_meta_test_types cascade;
drop view clin.v_unified_test_types cascade;
drop view clin.v_test_types cascade;
\set ON_ERROR_STOP 1

create view clin.v_test_types as
select
	-- original test type
	c_tt.pk
		as pk_test_type,
	c_tt.abbrev,
	c_tt.name,
	c_tt.loinc,
	c_tt.conversion_unit,
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
	(select array_agg(pk) from clin.test_panel c_tp where c_tt.pk = any(c_tp.fk_test_types)) as pk_test_panels,

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
select gm.log_script_insertion('v18-clin-v_test_types.sql', '18.0');
