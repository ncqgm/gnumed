-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.procedure.fk_org_unit is 'links to the or unit the procedure was performed at';

-- create "hospitals" in dem.org/dem.org_unit
-- orgs
insert into dem.org (description, fk_category)
select
	c_p.clin_where,
	(select pk from dem.org_category d_oc where d_oc.description = 'Medical Practice')
from
	clin.procedure c_p
where
	not exists (select 1 from dem.org where dem.org.description = c_p.clin_where)
;
-- units
insert into dem.org_unit (fk_org, description)
select
	(select pk from dem.org where dem.org.description = c_p.clin_where),
	c_p.clin_where
from
	clin.procedure c_p
where
	not exists (
		select 1 from dem.org_unit
		where
			dem.org_unit.description = c_p.clin_where
				and
			fk_org = (select pk from dem.org where dem.org.description = c_p.clin_where)
	)
;

-- add foreign key
alter table clin.procedure
	add foreign key (fk_org_unit)
		references dem.org_unit(pk)
		on update cascade
		on delete restrict;

-- link hospital stays to orgs
update clin.procedure set
	fk_org_unit = (
		select pk from dem.org_unit d_ou where d_ou.description = clin_where
	)
;

-- add new constraint
alter table clin.procedure
	drop constraint if exists clin_procedure_lnk_org_or_stay cascade;

alter table clin.procedure
	add constraint clin_procedure_lnk_org_or_stay check (
		((fk_hospital_stay is NULL) AND (fk_org_unit is not NULL))
			OR
		((fk_hospital_stay is not NULL) AND (fk_org_unit is NULL))
	)
;

-- drop old column
alter table clin.procedure drop column if exists clin_where cascade;

-- --------------------------------------------------------------
-- rewrite views + grants

\unset ON_ERROR_STOP
drop view clin.v_pat_procedures cascade;
drop view clin.v_procedures cascade;
drop view clin.v_procedures_at_hospital cascade;
drop view clin.v_procedures_not_at_hospital cascade;
\set ON_ERROR_STOP 1

create view clin.v_procedures_at_hospital as

select
	c_pr.pk
		as pk_procedure,
	c_enc.fk_patient
		as pk_patient,
	c_pr.soap_cat,
	c_pr.clin_when,
	c_pr.clin_end,
	c_pr.is_ongoing,
	c_pr.narrative
		as performed_procedure,
	c_vhs.ward
		as unit,
	c_vhs.hospital
		as organization,
	c_ep.description
		as episode,
	c_hi.description
		as health_issue,
	c_pr.modified_when
		as modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_pr.modified_by),
		'<' || c_pr.modified_by || '>'
	)
		as modified_by,
	c_pr.row_version,
	c_pr.fk_encounter
		as pk_encounter,
	c_pr.fk_episode
		as pk_episode,
	c_pr.fk_hospital_stay
		as pk_hospital_stay,
	c_ep.fk_health_issue
		as pk_health_issue,
	c_vhs.pk_org
		as pk_org,
	c_vhs.pk_org_unit
		as pk_org_unit,
	coalesce (
		(select array_agg(c_lc2p.fk_generic_code) from clin.lnk_code2procedure c_lc2p where c_lc2p.fk_item = c_pr.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes,
	c_pr.xmin as xmin_procedure
from
	clin.procedure c_pr
		inner join clin.encounter c_enc on c_pr.fk_encounter = c_enc.pk
			inner join clin.episode c_ep on c_pr.fk_episode = c_ep.pk
				left join clin.health_issue c_hi on c_ep.fk_health_issue = c_hi.pk
					left join clin.v_hospital_stays c_vhs on c_pr.fk_hospital_stay = c_vhs.pk_hospital_stay
where
	c_pr.fk_hospital_stay is not NULL
;


create view clin.v_procedures_not_at_hospital as

select
	c_pr.pk
		as pk_procedure,
	c_enc.fk_patient
		as pk_patient,
	c_pr.soap_cat,
	c_pr.clin_when,
	c_pr.clin_end,
	c_pr.is_ongoing,
	c_pr.narrative
		as performed_procedure,
	d_ou.description
		as unit,
	d_o.description
		as organization,
	c_ep.description
		as episode,
	c_hi.description
		as health_issue,
	c_pr.modified_when
		as modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_pr.modified_by),
		'<' || c_pr.modified_by || '>'
	)
		as modified_by,
	c_pr.row_version,
	c_pr.fk_encounter
		as pk_encounter,
	c_pr.fk_episode
		as pk_episode,
	c_pr.fk_hospital_stay
		as pk_hospital_stay,
	c_ep.fk_health_issue
		as pk_health_issue,
	d_o.pk
		as pk_org,
	d_ou.pk
		as pk_org_unit,
	coalesce (
		(select array_agg(c_lc2p.fk_generic_code) from clin.lnk_code2procedure c_lc2p where c_lc2p.fk_item = c_pr.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes,
	c_pr.xmin as xmin_procedure
from
	clin.procedure c_pr
		inner join clin.encounter c_enc on c_pr.fk_encounter = c_enc.pk
			inner join clin.episode c_ep on c_pr.fk_episode = c_ep.pk
				left join clin.health_issue c_hi on c_ep.fk_health_issue = c_hi.pk
					left join dem.org_unit d_ou on (d_ou.pk = c_pr.fk_org_unit)
						left join dem.org d_o on (d_o.pk = d_ou.fk_org)
where
	c_pr.fk_hospital_stay is NULL
;


create view clin.v_procedures as
select * from clin.v_procedures_at_hospital
	union all
select * from clin.v_procedures_not_at_hospital
;


grant select on clin.v_procedures_at_hospital TO GROUP "gm-doctors";
grant select on clin.v_procedures_not_at_hospital TO GROUP "gm-doctors";
grant select on clin.v_procedures TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-procedure-dynamic.sql', '19.0');
