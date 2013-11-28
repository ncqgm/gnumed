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
comment on column clin.hospital_stay.fk_org_unit is 'links to the hospital the patient was admitted to';

alter table clin.hospital_stay
	add foreign key (fk_org_unit)
		references dem.org_unit(pk)
		on update cascade
		on delete restrict;


-- create function for populating the foreign key
drop function if exists staging.populate_hospital_stay_FKs() cascade;

create function staging.populate_hospital_stay_FKs()
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_stay_row record;
	_pk_org integer;
	_pk_unit integer;
	_pk_cat integer;
	_org text;
	_unit text;
BEGIN
	FOR _stay_row IN
		select * from clin.hospital_stay
	LOOP
		insert into dem.org_category (description)
		select ''Hospital''::text where not exists (
			select 1 from dem.org_category where description = ''Hospital''
		);
		select pk into _pk_cat from dem.org_category where description = ''Hospital'';

		IF gm.is_null_or_blank_string(_stay_row.narrative) IS TRUE THEN
			_org := ''unknown hospital'';
		ELSE
			_org := _stay_row.narrative;
		END IF;

		_unit := ''unit of stay #'' || _stay_row.pk;

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

		update clin.hospital_stay set fk_org_unit = _pk_unit where pk = _stay_row.pk;
	END LOOP;
	return TRUE;
END;';


select staging.populate_hospital_stay_FKs();

drop function if exists staging.populate_hospital_stay_FKs() cascade;

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
