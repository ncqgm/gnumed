-- DDL structure of drug database for the gnumed project
-- Copyright 2000, 2001, 2002 by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- This is a complete redesign/rewrite since the October 2001 version 
--
-- usage:
--	log into psql (database gnumed OR drugs)  as administrator
--	run the script from the prompt with "\i drugs.sql"
--=====================================================================

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmdrugs.sql,v $
-- $Revision: 1.14 $ $Date: 2002-09-29 10:20:14 $ $Author: ncq $
-- ============================================================
-- $Log: gmdrugs.sql,v $
-- Revision 1.14  2002-09-29 10:20:14  ncq
-- - added code_systems.revision
--
-- Revision 1.13  2002/09/29 08:16:05  hherb
-- Complete rewrite: clean separation of drug reference and clinical data
-- such as prescriptions. Most issues now country/regulation independend with
-- facilities for internationalization.
--



create table drug_class(
	id serial primary key,
	category char check (category in ('t', 's')), 
	description text,
	comment text
);
comment on table drug_class is
'drug classes of specified categories';
comment on column drug_class.category is
'category of this class (t = therapeutic class, s = substance class)';
comment on column drug_class.description is
'name of this drug class (depending on category: beta blocker, antihistamine ...)';


create table drug_warning_categories(
	id serial primary key,
	description text,
	comment text
);
comment on table drug_warning_categories is
'enumeration of categories of warnings associated with a specific drug (as in product information)';
comment on column drug_warning_categories.description is
'the warning category such as "pregnancy", "lactation", "renal" ...';

-- I18N!
insert into drug_warning_categories(description) values('general');
insert into drug_warning_categories(description) values('pregnancy');
insert into drug_warning_categories(description) values('lactation');	
insert into drug_warning_categories(description) values('children');
insert into drug_warning_categories(description) values('elderly');
insert into drug_warning_categories(description) values('renal');
insert into drug_warning_categories(description) values('hepatic');


create table drug_warning(
	id serial primary key,
	id_warning integer references drug_warning_categories(id),
	code char(4),
	details text
);
comment on table drug_warning is
'any warning associated with a specific drug';
comment on column drug_warning.code is
'severity of the warning (like the the A,B,C,D scheme for pregnancy related warnings)';
comment on column drug_warning.code is
'could have been implemented as foreign key to a table of severity codes, but was considered uneccessary';

create table drug_information(
	id serial primary key,
	provider_code char check (provider_code in ('g', 'm', 'o')),
	target char check (target in ('h', 'p')),
	info text,
	comment text
);

comment on table drug_information is
'any product information about a specific drug in HTML format';
comment on column drug_information.provider_code is
'who provided this information: g=generic, m=manufacturer, o=other. If "other", references provided in the "info" text';
comment on column drug_information.target is
'the target of this information: h=health professional, p=patient';
comment on column drug_information.info is
'the drug product information in HTML format';


create table generic_drug(
	id serial primary key,
	is_compound boolean default 'n',
	name varchar(60),
	indication text,
	considerations text,
	dosage text,
	practice_points text,
	comment text
);
comment on table generic_drug is 
'A generic drug, either single substance or compound';
comment on column generic_drug.is_compound is
'false if this drug is based on a single substance (like Trimethoprim), true if based on a compound (like Cotrimoxazole)';
comment on column generic_drug.name is
'the generic name of this drug';


create table link_drug_class(
	drug integer references generic_drug(id),
	class integer references drug_class(id)
);
create index idx_link_drug_class on link_drug_class(drug, class);
comment on table link_drug_class is 
'A many-to-many pivot table linking classes to drugs';


create table link_drug_warning(
	drug integer references generic_drug(id),
	warning integer references drug_warning(id)
);
create index idx_link_drug_warning on link_drug_warning(drug, warning);
comment on table link_drug_warning is 
'A many-to-many pivot table linking warnings to drugs';


create table link_drug_information(
	drug integer references generic_drug(id),
	info integer references drug_information(id)
);
create index idx_link_drug_information on link_drug_information(drug, info);
comment on table link_drug_information is 
'A many-to-many pivot table linking product information to drugs';



create table drug_formulations(
	id serial primary key,
	description varchar(60),
	comment text
);
comment on table drug_formulations is
'presentations or formulations of drugs like "tablet", "capsule" ...';
comment on column drug_formulations.description is
'the formulation of the drug, such as "tablet", "cream", "suspension"';

--I18N!	
insert into drug_formulations(description) values ('tablet');
insert into drug_formulations(description) values ('capsule');
insert into drug_formulations(description) values ('syrup');
insert into drug_formulations(description) values ('suspension');
insert into drug_formulations(description) values ('powder');
insert into drug_formulations(description) values ('cream');
insert into drug_formulations(description) values ('ointment');
insert into drug_formulations(description) values ('lotion');
insert into drug_formulations(description) values ('suppository');
insert into drug_formulations(description) values ('solution');
insert into drug_formulations(description) values ('dermal patch');


create table drug_routes (
	id serial primary key,
	description varchar(60),
	abbreviation varchar(10),
	comment text
);
comment on table drug_routes is
'administration routes of drugs';
comment on column drug_routes.description is
'administration route of a drug like "oral", "sublingual", "intravenous" ...';

--I18N!
insert into drug_routes(description, abbreviation) values('oral', 'o.');
insert into drug_routes(description, abbreviation) values('sublingual', 's.l.');
insert into drug_routes(description, abbreviation) values('nasal', 'nas.');
insert into drug_routes(description, abbreviation) values('topical', 'top.');
insert into drug_routes(description, abbreviation) values('rectal', 'rect.');
insert into drug_routes(description, abbreviation) values('intravenous', 'i.v.');
insert into drug_routes(description, abbreviation) values('intramuscular', 'i.m.');
insert into drug_routes(description, abbreviation) values('subcutaneous', 's.c.');
insert into drug_routes(description, abbreviation) values('intraarterial', 'art.');
insert into drug_routes(description, abbreviation) values('intrathecal', 'i.th.');


create table drug_units (
	id serial primary key,
	unit varchar(30)
);
comment on table drug_units is
'(SI) units used to quantify/measure drugs';
comment on column drug_units.unit is
'(SI) units used to quantify/measure drugs like "mg", "ml"';
insert into drug_units(unit) values('ml');
insert into drug_units(unit) values('mg');
insert into drug_units(unit) values('mg/ml');
insert into drug_units(unit) values('U');
insert into drug_units(unit) values('IU');
insert into drug_units(unit) values('each');


create table adverse_effects(
	id serial primary key,
	severity integer,
	description text
);
comment on table adverse_effects is
'listing of possible adverse effects to drugs';
comment on column adverse_effects.severity is
'the severity of a reaction. The scale has yet to be aggreed upon.';
comment on column adverse_effects.description is
'the type of adverse effect like "pruritus", "hypotension", ...';


create table link_generic_drug_adverse_effects(
	id_drug integer references generic_drug(id),
	id_adverse_effect integer references adverse_effects(id),
	frequency char check(frequency in ('c', 'i', 'r'))
);
comment on table link_generic_drug_adverse_effects is
'many to many pivot table linking drugs to adverse effects';
comment on column link_generic_drug_adverse_effects.frequency is
'The likelihood this adverse effect happens: c=common, i=infrequent, r=rare';


create table interactions(
	id serial primary key,
	severity integer,
	description text,
	comment text
);
comment on table interactions is
'possible interactions between drugs';
comment on column interactions.severity is
'severity/significance of a potential interaction: the scale has yet to be agreed upon';
comment on column interactions.description is
'the type of interaction (like: "increases half life")';


create table link_drug_interactions(
	id serial primary key,
	id_drug integer references generic_drug(id),
	id_interacts_with integer references generic_drug(id),
	id_interaction integer references interactions(id),
	comment text
);
comment on table link_drug_interactions is
'many to many pivot table linking drugs and their interactions';


create table product(
	id serial primary key,
	id_generic_drug integer references generic_drug(id),
	id_formulation integer references drug_formulations(id),
	brandname varchar(60) default 'GENERIC',
	id_unit integer references drug_units(id),
	strength float,
	packing_unit integer references drug_units(id),
	package_size float,
	comment text
);
comment on table product is
'dispensable form of a generic drug including strength, package size etc';
comment on column product.brandname is
'the brand name as printed on the package';
comment on column product.strength is
'the strength of this formulation (units in column id_unit!)';
comment on column product.packing_unit is
'unit of drug "entities" as packed: for tablets and similar discrete formulations it should be the id of "each"';
comment on column product.package_size is
'the number of packing_units of this drug in this package';


create table available(
	id_product integer references product,
	iso_countrycode char(2),
	available_from date default null,
	banned date default null,
	comment text
);
comment on table available is
'availability of products in specific countries - this allows multinational drug databases without redundancy';
comment on column available.iso_countrycode is
'ISO country code of the country where this drug product is available';
comment on column available.available_from is
'date from which on the product is available in this country (if known)';
comment on column available.banned is
'date from which on this product is/was banned in the specified country, if applicable';

create table manufacturer(
	id serial primary key,
	name varchar(60),
	iso_countrycode char(2),
	address text,
	phone text,
	fax text,
	comment text
);
comment on table manufacturer is
'list of pharmaceutical manufacturers';
comment on column manufacturer.name is
'company name';
comment on column manufacturer.iso_countrycode is
'ISO country code of the location of this company';
comment on column manufacturer.address is
'complete printable address with embeded newline characters as "\n"';
comment on column manufacturer.phone is
'phone number of company';
comment on column manufacturer.fax is
'fax number of company';


create table link_product_manufacturer(
	id_product integer references product(id),
	id_manufacturer integer references manufacturer(id)
);
create index idx_link_product_manufacturer on link_product_manufacturer(id_product, id_manufacturer);
comment on table link_product_manufacturer is
'many to many pivot table linking drug products and manufacturers';


create table subsidies(
	id serial primary key,
	iso_countrycode char(2),
	name varchar(30),
	comment text
);
comment on table subsidies is
'listing of possible subsidies for drug products';
comment on column subsidies.iso_countrycode is
'ISO country code of the country where this subsidy applies';
comment on column subsidies.name is
'description of the subsidy (like PBS or RPBS in Australia)';


create table subsidized_products(
	id_product integer references product(id),
	id_subsidy integer references subsidies(id),
	max_qty integer default 1,
	max_rpt integer default 0,
	copayment float default 0.0,
	condition text,
	comment text
);
comment on table subsidized_products is
'listing of drug products that may attract a subsidy';
comment on column subsidized_products.max_qty is
'maximum quantiy of packaged units dispensed under subsidy for any one prescription';
comment on column subsidized_products.max_rpt is
'maximum number of repeat (refill) authorizations allowed on any one subsidised prescription (series)';
comment on column subsidized_products.copayment is 
'patient co-payment under subsidy regulation; if this is absolute or percentage is regulation dependend and not specified here';
comment on column subsidized_products.condition is
'condition that must be fulfilled so that this subsidy applies';


create table code_systems(
	id serial primary key,
	iso_country_code char(2) default '**',
	name varchar(30),
	version varchar(30),
	revision varchar(30)
);
comment on table code_systems is
'listing of disease coding systems used for drug indication listing';
comment on column code_systems.iso_country_code is
'ISO country code of country where this code system applies. Use "**" for wildcard';
comment on column code_systems.name is
'name of the code systme like ICD, ICPC';
comment on column code_systems.version is
'version of the code system, like "10" for ICD-10';
comment on column code_systems.revision is
'revision of the version of the coding system/classification';

insert into code_systems(name, version, revision) values ('ICD', '10', 'SGBV v1.3');
insert into code_systems(name, version) values ('ICPC', '2');


create table link_drug_indication(
	id serial primary key,
	id_drug integer references generic_drug,
	id_code_system integer references code_systems,
	indication_code char(8),
	comment text
);
create index idx_drug_indication on link_drug_indication(id_drug);
create index idx_indication_drug on link_drug_indication(indication_code);

comment on table link_drug_indication is
'many to many pivot table linking drugs and indications';
comment on column link_drug_indication.indication_code is
'code of the disease/indication in the specified code system';

