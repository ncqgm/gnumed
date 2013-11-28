-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
-- .fk_org_unit
comment on column clin.procedure.fk_org_unit is 'links to the or unit the procedure was performed at';

alter table clin.procedure
	add foreign key (fk_org_unit)
		references dem.org_unit(pk)
		on update cascade
		on delete restrict;


-- create function for populating the foreign key
drop function if exists staging.populate_procedure_FKs() cascade;

create function staging.populate_procedure_FKs()
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_proc_row record;
	_pk_org integer;
	_pk_unit integer;
	_pk_cat integer;
	_org text;
	_unit text;
BEGIN
	FOR _proc_row IN
		select * from clin.procedure where fk_hospital_stay is null
	LOOP
		insert into dem.org_category (description)
		select ''Point Of Care''::text where not exists (
			select 1 from dem.org_category where description = ''Point Of Care''
		);
		select pk into _pk_cat from dem.org_category where description = ''Point Of Care'';

		IF gm.is_null_or_blank_string(_proc_row.clin_where) IS TRUE THEN
			_org := ''org for unknown Point Of Care'';
			_unit := ''unknown Point Of Care'';
		ELSE
			_org := ''org for "'' || _proc_row.clin_where || ''"'';
			_unit := _proc_row.clin_where;
		END IF;

		select pk into _pk_org from dem.org where description = _org;
		IF _pk_org IS NULL THEN
			insert into dem.org (fk_category, description) values (_pk_cat, _org);
			select pk into _pk_org from dem.org where description = _org;
		END IF;

		select pk into _pk_unit from dem.org_unit where description = _unit and fk_org = _pk_org;
		IF _pk_unit IS NULL THEN
			insert into dem.org_unit (fk_org, description) values (_pk_org, _unit);
			select pk into _pk_unit from dem.org_unit where description = _unit and fk_org = _pk_org;
		END IF;

		update clin.procedure set fk_org_unit = _pk_unit where pk = _proc_row.pk;
	END LOOP;
	return TRUE;
END;';


select staging.populate_procedure_FKs();

drop function if exists staging.populate_procedure_FKs() cascade;


-- add new constraint
alter table clin.procedure drop constraint if exists single_location_definition cascade;
alter table clin.procedure drop constraint if exists clin_procedure_lnk_org_or_stay cascade;

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
