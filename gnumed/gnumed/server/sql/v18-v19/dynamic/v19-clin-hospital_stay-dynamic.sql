-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- de-crapify data
update clin.hospital_stay set
	narrative = 'unknown hospital [stay:' || pk || ']'
where
	gm.is_null_or_blank_string(narrative) is True
;

comment on column clin.hospital_stay.fk_org_unit is 'links to the hospital the patient was admitted to';

-- create "hospitals" in dem.org/dem.org_unit
-- orgs
insert into dem.org (description, fk_category)
select
	c_hs.narrative,
	(select pk from dem.org_category d_oc where d_oc.description = 'Hospital')
from
	clin.hospital_stay c_hs
where
	not exists (select 1 from dem.org where dem.org.description = c_hs.narrative)
;
-- units
insert into dem.org_unit (fk_org, description)
select
	(select pk from dem.org where dem.org.description = c_hs.narrative),
	c_hs.narrative
from
	clin.hospital_stay c_hs
where
	not exists (
		select 1 from dem.org_unit
		where
			dem.org_unit.description = c_hs.narrative
				and
			fk_org = (select pk from dem.org where dem.org.description = c_hs.narrative)
	)
;

-- add foreign key
alter table clin.hospital_stay
	add foreign key (fk_org_unit)
		references dem.org_unit(pk)
		on update cascade
		on delete restrict;

-- link hospital stays to orgs
update clin.hospital_stay set
	fk_org_unit = (
		select pk from dem.org_unit d_ou where d_ou.description = narrative
	)
;

-- set not null
alter table clin.hospital_stay
	alter column fk_org_unit
		set not null;

-- repurpose old column
update clin.hospital_stay set narrative = NULL;

comment on column clin.hospital_stay.narrative is 'a comment on the hospital stay';

-- --------------------------------------------------------------
-- rewrite views + grants

\unset ON_ERROR_STOP
drop view clin.v_pat_hospital_stays cascade;
drop view clin.v_hospital_stays cascade;
\set ON_ERROR_STOP 1

create view clin.v_hospital_stays as
select
	c_hs.pk
		as pk_hospital_stay,
	(select fk_patient from clin.encounter where pk = c_hs.fk_encounter)
		as pk_patient,
	d_o.description
		as hospital,
	d_ou.description
		as ward,
	c_hs.narrative
		as comment,
	c_hs.clin_when
		as admission,
	c_hs.discharge,
	c_hs.soap_cat
		as soap_cat,
	c_e.description
		as episode,
	c_hi.description
		as health_issue,
	c_hs.fk_encounter
		as pk_encounter,
	c_hs.fk_episode
		as pk_episode,
	c_hi.pk
		as pk_health_issue,
	c_hs.fk_org_unit
		as pk_org_unit,
	d_o.pk
		as pk_org,
	c_hs.modified_when
		as modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_hs.modified_by),
		'<' || c_hs.modified_by || '>'
	)
		as modified_by,
	c_hs.row_version,
	c_hs.xmin
		as xmin_hospital_stay
from
	clin.hospital_stay c_hs
		left join clin.episode c_e on (c_e.pk = c_hs.fk_episode)
			left join clin.health_issue c_hi on (c_hi.pk = c_e.fk_health_issue)
				left join dem.org_unit d_ou on (d_ou.pk = c_hs.fk_org_unit)
					left join dem.org d_o on (d_o.pk = d_ou.fk_org)
;

grant select on clin.v_hospital_stays to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-hospital_stay-dynamic.sql', '19.0');
