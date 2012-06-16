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
-- dem.org
select gm.add_table_for_notifies('dem'::name, 'org'::name);
select audit.add_table_for_audit('dem'::name, 'org'::name);


comment on table dem.org is
'Organizations at a conceptual level.';


-- .description
comment on column dem.org.description is
'High-level, conceptual description (= name) of organization, such as "University of Manchester".';

\unset ON_ERROR_STOP
alter table dem.org drop constraint org_sane_description cascade;
\set ON_ERROR_STOP 1

alter table dem.org
	add constraint org_sane_description check (
		gm.is_null_or_blank_string(description) is false
	)
;


-- .fk_category
-- for now, leave this nullable ;-)
alter table dem.org
	add foreign key (fk_category)
		references dem.org_category(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- dem.org_unit
select gm.add_table_for_notifies('dem'::name, 'org_unit'::name);
select audit.add_table_for_audit('dem'::name, 'org_unit'::name);


comment on table dem.org_unit is
'Actual branches/departments/offices/... of organizations.';


-- .description
comment on column dem.org_unit.description is
'Description (= name) of branch of organization, such as "Elms Street office of Jim Busser Praxis".';

\unset ON_ERROR_STOP
alter table dem.org_unit drop constraint org_unit_sane_description cascade;
alter table dem.org_unit drop constraint org_unit_uniq_per_org cascade;
\set ON_ERROR_STOP 1

alter table dem.org_unit
	add constraint org_unit_sane_description check (
		gm.is_null_or_blank_string(description) is false
	)
;

alter table dem.org_unit
	add constraint org_unit_uniq_per_org
		unique(fk_org, description)
;


-- .fk_org
alter table dem.org_unit
	alter column fk_org
		set not null;

alter table dem.org_unit
	add foreign key (fk_org)
		references dem.org(pk)
		on update cascade
		on delete restrict
;


-- .fk_address
--alter table dem.org_unit
--	alter column fk_address
--		set not null;

alter table dem.org_unit
	add foreign key (fk_address)
		references dem.address(id)
		on update cascade
		on delete restrict
;



-- .fk_category
-- for now, leave this nullable ;-)
alter table dem.org_unit
	add foreign key (fk_category)
		references dem.org_category(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- permissions
grant select, insert, update, delete on
	dem.org
	, dem.org_pk_seq
	, dem.org_unit
	, dem.org_unit_pk_seq
	, dem.org_category
	, dem.org_category_id_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- dem.lnk_org_unit2comm
select audit.add_table_for_audit('dem'::name, 'lnk_org_unit2comm'::name);


comment on table dem.lnk_org_unit2comm is
	'Comm channels per org unit.';


-- .fk_org_unit
alter table dem.lnk_org_unit2comm
	add foreign key (fk_org_unit)
		references dem.org(pk)
		on update cascade
		on delete restrict
;

alter table dem.lnk_org_unit2comm
	alter column fk_org_unit
		set not null
;


-- .fk_type
alter table dem.lnk_org_unit2comm
	add foreign key (fk_type)
		references dem.enum_comm_types(pk)
		on update cascade
		on delete restrict
;

alter table dem.lnk_org_unit2comm
	alter column fk_type
		set not null
;


-- .url
\unset ON_ERROR_STOP
alter table dem.org_unit2comm drop constraint lnk_org_unit2comm_sane_url cascade;
alter table dem.org_unit2comm drop constraint lnk_org_unit2comm_uniq_url cascade;
\set ON_ERROR_STOP 1

alter table dem.lnk_org_unit2comm
	add constraint lnk_org_unit2comm_sane_url check (
		gm.is_null_or_blank_string(url) is false
	)
;

alter table dem.lnk_org_unit2comm
	add constraint lnk_org_unit2comm_uniq_url
		unique(fk_org_unit, url, fk_type)
;


-- .is_confidential
alter table dem.lnk_org_unit2comm
	alter column is_confidential
		set not null
;

alter table dem.lnk_org_unit2comm
	alter column is_confidential
		set default false
;


-- permissions
grant select, insert, update, delete on dem.lnk_org_unit2comm to group "gm-public";

-- --------------------------------------------------------------
-- dem.lnk_org_unit2ext_id
select audit.add_table_for_audit('dem'::name, 'lnk_org_unit2ext_id'::name);


comment on table dem.lnk_org_unit2ext_id is
	'External IDs per org unit.';


-- .fk_org_unit
alter table dem.lnk_org_unit2ext_id
	add foreign key (fk_org_unit)
		references dem.org(pk)
		on update cascade
		on delete restrict
;

alter table dem.lnk_org_unit2ext_id
	alter column fk_org_unit
		set not null
;


-- .fk_type
alter table dem.lnk_org_unit2ext_id
	add foreign key (fk_type)
		references dem.enum_ext_id_types(pk)
		on update cascade
		on delete restrict
;

alter table dem.lnk_org_unit2ext_id
	alter column fk_type
		set not null
;


-- .external_id
\unset ON_ERROR_STOP
alter table dem.org_unit2ext_id drop constraint lnk_org_unit2ext_id_sane_id cascade;
alter table dem.org_unit2ext_id drop constraint lnk_org_unit2ext_id_uniq_id cascade;
\set ON_ERROR_STOP 1

alter table dem.lnk_org_unit2ext_id
	add constraint lnk_org_unit2ext_id_sane_id check (
		gm.is_null_or_blank_string(external_id) is false
	)
;

alter table dem.lnk_org_unit2ext_id
	add constraint lnk_org_unit2ext_id_uniq_id
		unique(fk_org_unit, external_id, fk_type)
;


-- .comment
\unset ON_ERROR_STOP
alter table dem.org_unit2ext_id drop constraint lnk_org_unit2ext_id_sane_comment cascade;
\set ON_ERROR_STOP 1

alter table dem.lnk_org_unit2ext_id
	add constraint lnk_org_unit2ext_id_sane_comment check (
		gm.is_null_or_non_empty_string(comment) is true
	)
;


-- permissions
grant select, insert, update, delete on dem.lnk_org_unit2ext_id to group "gm-public";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_orgs cascade;
drop view dem.v_org_units cascade;
drop view dem.lnk_org2address cascade;
\set ON_ERROR_STOP 1



create view dem.v_orgs as
select
	org.pk
		as pk_org,
	org.description
		as organization,
	doc.description
		as category,
	_(doc.description)
		as l10n_category,
	org.fk_category
		as pk_category_org,
	org.xmin
		as xmin_org
from
	dem.org org
		left join dem.org_category doc on (org.fk_category = doc.pk)
;



create view dem.v_org_units as

select
	dou.pk
		as pk_org_unit,
	dvo.organization,
	dou.description
		as unit,
	dvo.category
		as organization_category,
	_(dvo.category)
		as l10n_organization_category,
	doc.description
		as unit_category,
	_(doc.description)
		as l10n_unit_category,
	dvo.pk_org,
	dvo.pk_category_org,
	dou.fk_category
		as pk_category_unit,
	dou.fk_address
		as pk_address,
	dou.xmin
		as xmin_org_unit
from
	dem.org_unit dou
		left join dem.v_orgs dvo on (dou.fk_org = dvo.pk_org)
			left join dem.org_category doc on (dou.fk_category = doc.pk)
;



grant select on
	dem.v_orgs,
	dem.v_org_units
to group "gm-public";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP

insert into dem.org_category (description) values ('Government');
insert into dem.org_category (description) values ('Hospital');
insert into dem.org_category (description) values ('Ward');
insert into dem.org_category (description) values ('Practice');
insert into dem.org_category (description) values ('Surgery');
insert into dem.org_category (description) values ('Medical Practice');
insert into dem.org_category (description) values ('Physical Therapy Practice');
insert into dem.org_category (description) values ('Occupational Therapy Practice');
insert into dem.org_category (description) values ('Laboratory');



insert into dem.org (description, fk_category) values (
	'Ministry of Public Health',
	(select pk from dem.org_category where description = 'Government')
);

-- Starship Enterprise address
insert into dem.org (description, fk_category) values (
	'Starfleet Central',
	(select pk from dem.org_category where description = 'Hospital')
);



select dem.create_address('117', 'Golden Gate Drive', 'SF 278 CA', 'San Francisco', 'CA', 'US', NULL);
select dem.create_address('31', 'Galley 4a', 'NCC-1701-E', 'Starship Enterprise', 'CA', 'US', NULL);
update dem.street set suburb = 'Deck 7' where name = 'Galley 4a';
update dem.address set
	addendum = 'typically in Space'
where id_street = (
	select id from dem.street where name = 'Galley 4a' and postcode = 'NCC-1701-E'
);



insert into dem.org_unit (description, fk_org, fk_category, fk_address) values (
	'Ward A-II',
	(select pk from dem.org where description = 'Starfleet Central'),
	(select pk from dem.org_category where description = 'Ward'),
	(select pk_address from dem.v_address where street = 'Golden Gate Drive' and postcode = 'SF 278 CA')
);

insert into dem.org_unit (description, fk_org, fk_category, fk_address) values (
	'Enterprise Sickbay',
	(select pk from dem.org where description = 'Starfleet Central'),
	(select pk from dem.org_category where description = 'Ward'),
	(select pk_address from dem.v_address where street = 'Galley 4a' and postcode = 'NCC-1701-E')
);



-- Notfallzentrum Riebeckstrasse
insert into dem.org (description, fk_category) values (
	'Notfallzentrum THONBERGKLINIKmvz',
	(select pk from dem.org_category where description = 'Medical Practice')
);

select dem.create_address('65', 'Riebeckstraße', '04317', 'Leipzig', 'SN', 'DE', 'Parterre');
update dem.street set suburb = 'Reudnitz-Thonberg' where name like 'Riebeckstra%' and postcode = '04317';

insert into dem.org_unit (description, fk_org, fk_category, fk_address) values (
	'Chirurgische Gemeinschaftspraxis',
	(select pk from dem.org where description = 'Notfallzentrum THONBERGKLINIKmvz'),
	(select pk from dem.org_category where description = 'Medical Practice'),
	(select pk_address from dem.v_address where street like 'Riebeckstra%' and postcode = '04317' and number = '65')
);

\set ON_ERROR_STOP 1



select i18n.upd_tx('de', 'Ministry of Public Health', 'Gesundheitsministerium');
select i18n.upd_tx('de', 'Hospital', 'Krankenhaus');
select i18n.upd_tx('de', 'Ward', 'Station');
select i18n.upd_tx('de', 'Practice', 'Praxis');
select i18n.upd_tx('de', 'Surgery', 'Praxis');
select i18n.upd_tx('de', 'Medical Practice', 'Praxis');
select i18n.upd_tx('de', 'Physical Therapy Practice', 'Physiotherapiepraxis');
select i18n.upd_tx('de', 'Occupational Therapy Practice', 'Ergotherapiepraxis');
select i18n.upd_tx('de', 'Laboratory', 'Labor');

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-org_handling-dynamic.sql', '1.2');

-- ==============================================================
