-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
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
'Organisations at a conceptual level.';


-- .description
comment on column dem.org.description is
'High-level, conceptual description (= name) of organisation, such as "University of Manchester".';

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
'Actual branches/departments/offices/... of organisations.';


-- .description
comment on column dem.org_unit.description is
'Description (= name) of branch of organisation, such as "Elms Street office of Jim Busser Praxis".';

alter table dem.org_unit
	add constraint org_unit_sane_description check (
		gm.is_null_or_blank_string(description) is false
	)
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
alter table dem.org_unit
	alter column fk_address
		set not null;

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
	, dem.org_unit
	, dem.org_category
to group "gm-doctors";

-- --------------------------------------------------------------
alter table dem.lnk_org2comm
	add foreign key (fk_org)
		references dem.org(pk)
		on update cascade
		on delete restrict
;


alter table dem.lnk_org2comm
	alter column fk_type
		set not null
;


alter table dem.lnk_org2comm
	add constraint lnk_org2comm_sane_url check (
		gm.is_null_or_blank_string(url) is false
	)
;

-- --------------------------------------------------------------
alter table dem.lnk_org2ext_id
	add foreign key (fk_org)
		references dem.org(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_org cascade;
drop view dem.v_org_units cascade;
\set ON_ERROR_STOP 1



create view dem.v_org as
select
	org.pk
		as pk_org,
	org.description
		as organisation,
	doc.description
		as category,
	_(doc.description)
		as l10n_category,
	org.fk_category
		as pk_category_org
from
	dem.org org
		left join dem.org_category doc on (org.fk_category = doc.pk)
;



create view dem.v_org_units as

select
	dou.pk
		as pk_org_unit,
	dvo.organisation,
	dou.description
		as unit,
	dvo.category
		as organisation_category,
	_(dvo.category)
		as l10n_organisation_category,
	doc.description
		as unit_category,
	_(doc.description)
		as l10n_unit_category,
	dvo.pk_org,
	dvo.pk_category_org,
	dou.fk_category
		as pk_category_unit,
	dou.fk_address
		as pk_address
from
	dem.org_unit dou
		left join dem.v_org dvo on (dou.fk_org = dvo.pk_org)
			left join dem.org_category doc on (dou.fk_category = doc.pk)
;



grant select on
	dem.v_org,
	dem.v_org_units
to group "gm-public";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP

insert into dem.org_category (description) values ('Government');
insert into dem.org_category (description) values ('Hospital');
insert into dem.org_category (description) values ('Ward');



insert into dem.org (description, fk_category) values (
	'Ministry of Public Health',
	(select pk from dem.org_category where description = 'Government')
);

insert into dem.org (description, fk_category) values (
	'Starfleet Central',
	(select pk from dem.org_category where description = 'Hospital')
);



select dem.create_address('117', 'Golden Gate Drive', 'SF 278 CA', 'San Francisco', 'CA', 'US', NULL);
select dem.create_address('1', 'Deck 7', 'NCC-1701-E', 'San Francisco', 'CA', 'US', NULL);



insert into dem.org_unit (description, fk_org, fk_category, fk_address) values (
	'Ward A-II',
	(select pk from dem.org where description = 'Starfleet Central'),
	(select pk from dem.org_category where description = 'Ward'),
	(select pk_address from dem.v_address where street = 'Golden Gate Drive' and postcode = 'SF 278 CA')
);

insert into dem.org_unit (description, fk_org, fk_category, fk_address) values (
	'Enterprise Sickbay Ward',
	(select pk from dem.org where description = 'Starfleet Central'),
	(select pk from dem.org_category where description = 'Ward'),
	(select pk_address from dem.v_address where street = 'Deck 7' and postcode = 'NCC-1701-E')
);

\set ON_ERROR_STOP 1



select i18n.upd_tx('de', 'Ministry of Public Health', 'Gesundheitsministerium');
select i18n.upd_tx('de', 'Hospital', 'Krankenhaus');
select i18n.upd_tx('de', 'Ward', 'Station');

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-org_handling-dynamic.sql', '1.2');

-- ==============================================================
