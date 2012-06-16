-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.fhx_relation_type (
	pk serial primary key,
	description text,
	is_genetic boolean
) inherits (audit.audit_fields);

insert into clin.fhx_relation_type (
	description,
	is_genetic
) select distinct on (narrative)
	c_hxf.narrative,
	True
 from
 	clin.clin_hx_family c_hxf
;

-- --------------------------------------------------------------
alter table clin.clin_hx_family
	add column fk_relation_type integer;

alter table audit.log_clin_hx_family
	add column fk_relation_type integer;

update clin.clin_hx_family set
	fk_relation_type = (
		select pk
		from clin.fhx_relation_type c_fhxrt
		where
			c_fhxrt.description = narrative
	)
;

-- --------------------------------------------------------------
alter table clin.clin_hx_family
	add column age_noted text;

alter table audit.log_clin_hx_family
	add column age_noted text;


alter table clin.clin_hx_family
	add column age_of_death interval;

alter table audit.log_clin_hx_family
	add column age_of_death interval;


alter table clin.clin_hx_family
	add column contributed_to_death boolean;

alter table audit.log_clin_hx_family
	add column contributed_to_death boolean;

-- --------------------------------------------------------------
alter table clin.clin_hx_family
	add column name_relative text;

alter table audit.log_clin_hx_family
	add column name_relative text;

-- --------------------------------------------------------------
alter table clin.clin_hx_family
	add column dob_relative timestamp with time zone;

alter table audit.log_clin_hx_family
	add column dob_relative timestamp with time zone;


alter table clin.clin_hx_family
	add column comment text;

alter table audit.log_clin_hx_family
	add column comment text;

-- --------------------------------------------------------------
update clin.clin_hx_family set
	narrative = c_hfi.condition,
	age_noted = c_hfi.age_noted,
	age_of_death = c_hfi.age_of_death,
	contributed_to_death = c_hfi.is_cause_of_death,
	name_relative = c_hfi.name_relative,
	dob_relative = c_hfi.dob_relative
from
	clin.hx_family_item c_hfi
where
 	c_hfi.pk = fk_hx_family_item
;

-- --------------------------------------------------------------
alter table clin.clin_hx_family
	drop column fk_hx_family_item cascade;

alter table audit.log_clin_hx_family
	drop column fk_hx_family_item;

-- --------------------------------------------------------------
alter table clin.clin_hx_family
	rename to family_history;


alter table audit.log_clin_hx_family
	rename to log_family_history;


drop table clin.hx_family_item cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-family_history-static.sql', 'v16.0');
