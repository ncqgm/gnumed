-- DDL structure of auditing system drug database for the gnumed project
-- Copyright 2002 by Ian Haywood
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- usage:
--	log into psql (database gnumed OR drugs)  as administrator
--	run the script from the prompt with "\i drugs.admin.sql" AFTER gmdrugs.sql
--=====================================================================
-- Revision 0.1 2002/10/28 ihaywood 
--
-- this is a special supplement to gmdrugs to allow editing and auditing.
-- it is seperated to preserve the intregity of gmdrugs.sql
-- tables for auditing. This is a parallel auditing system just for the 
-- drug databases. The users are the creators of the database, 
-- and may have no overlap with the users on deployed databases.

-- NOT FINISHED, don't use use yet.

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1


create table users 
(
	login name,
	public_key text,
	title varchar (100),
	password_expiry date,
	iso_countrycode char (2)
);

comment on table users is 'extra data about database users';
comment on column users.public_key is 'armoured GPG public key of this user';
comment on column users.title is 'full name and qualifications';
comment on column users.password_expiry is 'the date the password expires';
comment on column users.iso_countrycode is 'the users country';

insert into users values ('ian', NULL, 'Dr. Ian Haywood, MBBS', '31 Dec 2002', 'au');
insert into users values ('hherb', NULL, 'Dr. Horst Herb, MBBS', '31 Dec 2002', 'au');
insert into users values ('dguest', NULL, 'Dr. David Guest', '31 Dec 2002', 'au');
insert into users values ('ncq', NULL, 'Dr. Karsten Hibert, MBBS', '31 Dec 2002', 'de');
insert into users values ('hilmar', NULL, 'Dr. Hilmar Berger, MBBS', '31 Dec 2002', 'de');
insert into users values ('guest', NULL, 'Guest User (NOT Dr. David Guest)', NULL, '**');

-- groups of users -- superuser must do this!
--create group contributors;
--create group browsers;

grant all on drug_dosage to group contributors;
grant all on generic_drug_name to group contributors;
grant all on link_country_drug_name to group contributors;
grant all on link_compound_generics to group contributors;
grant all on link_drug_adverse_effects to group contributors;
grant all on link_drug_class to group contributors;
grant all on link_drug_disease_interactions to group contributors;
grant all on link_drug_indication to group contributors;
grant all on link_drug_information to group contributors;
grant all on link_drug_interactions to group contributors;
grant all on link_drug_warning to group contributors;
grant all on link_flag_product to group contributors;
grant all on link_product_component to group contributors;
grant all on link_product_manufacturer to group contributors;
grant all on product to group contributors;
grant all on subsidized_products to group contributors;
grant all on substance_dosage to group contributors;
grant all on drug_warning to group contributors;
grant all on drug_information to group contributors;
grant all on drug_element to group contributors;
grant all on conditions to group contributors;
grant all on available to group contributors;
grant all on manufacturer to group contributors;
grant all on info_reference to group contributors;
grant all on interactions to group contributors;
grant all on adverse_effects to group contributors;
grant all on package_size to group contributors;

grant select on drug_dosage to group browsers;
grant select on generic_drug_name to group browsers;
grant select on link_country_drug_name to group browsers;
grant select on link_compound_generics to group browsers;
grant select on link_drug_adverse_effects to group browsers;
grant select on link_drug_class to group browsers;
grant select on link_drug_disease_interactions to group browsers;
grant select on link_drug_indication to group browsers;
grant select on link_drug_information to group browsers;
grant select on link_drug_interactions to group browsers;
grant select on link_drug_warning to group browsers;
grant select on link_flag_product to group browsers;
grant select on link_product_component to group browsers;
grant select on link_product_manufacturer to group browsers;
grant select on product to group browsers;
grant select on subsidized_products to group browsers;
grant select on substance_dosage to group browsers;
grant select on drug_warning to group browsers;
grant select on drug_information to group browsers;
grant select on drug_element to group browsers;
grant select on conditions to group browsers;
grant select on available to group browsers;
grant select on manufacturer to group browsers;
grant select on info_reference to group browsers;
grant select on interactions to group browsers;
grant select on adverse_effects to group browsers;
grant select on package_size to group browsers;

grant select on disease_code to public;
grant select on code_systems to public;
grant select on drug_flags to public;
grant select on drug_formulations to public;
grant select on drug_routes to public;
grant select on drug_units to public;
grant select on information_topic to public;
grant select on drug_warning_categories to public;
grant select on subsidies to public;
grant select on users to public;

create table comments
(
	id serial primary key,
	table_name name,
	table_row integer,
	stamp datetime default current_timestamp,
	who name default current_user,
	comment text,
	source integer references info_reference (id),
	signature text 
);


create table changelog
(
	id serial primary key,
	id_drug integer references drug_element (id),
	stamp timestamp default current_timestamp,
	who name default current_user,
	comment text,
	revert text
);

comment on table changelog is
'changelog for the whole database';
comment on column changelog.id_drug is
'reference to drug, if relevant'; 
comment on column changelog.comment is
'auto-generated description of the change'; 
comment on column changelog.revert is
'semicolon-separated list of SQL commands to undo the 
changes so described.';  



