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
-- $Revision: 1.18 $ $Date: 2002-10-28 04:39:07 $ $Author: ihaywood $
-- ============================================================
-- $Log: gmdrugs.sql,v $
-- Revision 1.18  2002-10-28 04:39:07  ihaywood
-- added drug_flags and minor changes
--
-- Revision 1.17  2002/10/26 12:38:20  ihaywood
-- Changes to gmdrugs.sql please review
--
-- Revision 1.17 2002/10/20 ihaywood 
-- additions for versioning and attribution of data
-- Revision 1.16  2002/10/07 07:23:43  hherb
-- generic_drug further normalized (drug names no separate entities to allow for synonyms and translations)
-- compound drug components now linked to compound drugs
--
-- Revision 1.14  2002/09/29 10:20:14  ncq
-- - added code_systems.revision
--
-- Revision 1.13  2002/09/29 08:16:05  hherb
-- Complete rewrite: clean separation of drug reference and clinical data
-- such as prescriptions. Most issues now country/regulation independend with
-- facilities for internationalization.
--

create table info_reference(
	id serial primary key,
	source_category char check (source_category in ('p', 'a', 'i', 'm', 'o', 's')),
	description text
);
comment on table info_reference is
'Source of any reference information in this database';
comment on column info_reference.source_category is
'p=peer reviewed, a=official authority, i=independend source, m=manufacturer, o=other, s=self defined';
comment on column info_reference.description is
'URL or address or similar informtion allowing to reproduce the source of information';

-- couple to examples
insert into info_reference (source_category, description) values ('i', 'Rang, Dale, and Ritter <i>Pharmacology</i>, 1999'); 

create table audited_table
(
	id serial primary key
);

comment on table audited_table is 'ancestor table, inherited by all tables that need to be audited.';


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


create table drug_element (
	id serial primary key,
	category char check (category in ('t', 'p', 's', 'c')),
	description text
);

comment on table drug_element is 'collection of all drug elements: classes, compounds, and substances';

comment on column drug_element.category is 't = therapeutic class, p = pharmaceutical class, s = substance, c = compound';

create view drug_class as select * from drug_element where category = 't' or category = 'p';

comment on view drug_class is
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
	id_reference integer references info_reference(id) default NULL,
	code char(4),
	details text
);
comment on table drug_warning is
'any warning associated with a specific drug';
comment on column drug_warning.code is
'severity of the warning (like the the A,B,C,D scheme for pregnancy related warnings)';
comment on column drug_warning.code is
'could have been implemented as foreign key to a table of severity codes, but was considered uneccessary';

create table information_topic
(
	id serial,
	title varchar (60),
	target char check (target in ('h', 'p'))
);

comment on table information_topic is 'topics for drug information, such as pharmaco-kinetics, indications, etc.';

comment on column information_topic.target is
'the target of this information: h=health professional, p=patient';

insert into information_topic (title, target) values ('general', 'h');
insert into information_topic (title, target) values ('pharmaco-kinetics', 'h');
insert into information_topic (title, target) values ('indications', 'h');
insert into information_topic (title, target) values ('action', 'h');
insert into information_topic (title, target) values ('chemical structure', 'h'); -- perhaps in ChemML or similar.
insert into information_topic (title, target) values ('side-effects', 'p');
insert into information_topic (title, target) values ('general', 'p');


create table drug_information(
	id serial primary key,
	id_info_reference integer references info_reference(id),
	info text,
	id_topic integer references information_topic (id),
	comment text
);
comment on table drug_information is
'any product information about a specific drug in HTML format';
comment on column drug_information.info is
'the drug product information in HTML format';


create view generic_drug as select id, 
	category = 'c' as is_compound from drug_element where category = 'c' or category = 's';
comment on view generic_drug is
'A generic drug, either single substance or compound';
comment on column generic_drug.is_compound is
'false if this drug is based on a single substance (like Trimethoprim), true if based on a compound (like Cotrimoxazole)';


create table generic_drug_name(
	id serial primary key,
	id_drug integer references drug_element (id),
	name varchar(60),
	comment text
);
comment on table generic_drug_name is
'this table allows synonyms / dictionary functionality for generic drug names';
comment on column generic_drug_name.name is
'the generic name of this drug';

drop function get_drug_name (integer);

create function get_drug_name (integer) returns text as '
r = plpy.execute ("select category = ''p'' or category = ''t'' as is_drug, description from drug_element where id = %s" % args[0])
if r[0]["is_drug"] == "t":
 return r[0]["description"]
else:
 # drug name linked to country "**"
 r = plpy.execute ("select name from generic_drug_name, link_country_drug_name where iso_countrycode = ''**'' and id_drug_name = generic_drug_name.id and id_drug = %s" % args[0])
 if len (r) > 0:
  return r[0]["name"]
 # drug name linked to no country
 r = plpy.execute ("select name from generic_drug_name where id_drug = %s and not exists (select * from link_country_drug_name where id_drug_name = generic_drug_name.id)" % args[0])
 if len (r) > 0:
  return r[0]["name"]
 # in desperation, ANY drug name
 r = plpy.execute ("select name from generic_drug_name where id_drug = %s" % args[0])
 if len (r) > 0:
  return r[0]["name"]
 else:
  return "NONAME"
' language 'plpython';

comment on function get_drug_name (integer) is 'guaranteed returns a name for a drug/class';

create table link_compound_generics(
	id_compound integer references drug_element(id) not null,
	id_component integer references drug_element(id) not null
);
create index idx_link_compound_generics on link_compound_generics(id_compound, id_component);
comment on table link_compound_generics is
'links singular generic drugs to a compound drug (like Trimethoprim and Sulfamethoxazole to Cotrimoxazole)';


create table link_country_drug_name(
	id_drug_name integer references generic_drug_name(id),
	iso_countrycode char(2)
);
create index idx_link_country_drug_name on link_country_drug_name(iso_countrycode, id_drug_name);
comment on table link_country_drug_name is
'indicates in which country a specific generic drug name is in use. ''**'' marks the international name';

create table drug_dosage(
	id serial,
	id_drug integer references drug_element (id),
	id_drug_warning_categories integer references drug_warning_categories(id) default NULL,
	id_info_reference integer references info_reference(id),
	id_drug_route integer references drug_routes (id),
	dosage_hints text
);

comment on table drug_dosage is
'A table linking drugs to dosage recommendations. This is the old link_drug_dosage. Refers to drugs, both compounds and single-substances.';
comment on column drug_dosage.id_drug_warning_categories is
'indicates whether this dosage is targeted for specific patients, like paediatric or renal impairment';
comment on column drug_dosage.dosage_hints is
'free text warnings, tips & hints regarding applying this dosage recommendation';

create table substance_dosage(
	id serial primary key,
	id_drug_dosage integer references drug_dosage (id), 
	id_drug_units integer references drug_units (id),
	id_component integer references drug_element (id), 
	dosage_type char check (dosage_type in ('*', 'w', 's', 'a')),
	dosage_start float,
	dosage_max float
);
comment on table substance_dosage is
'Dosage suggestion for a particular /substance/ (not compound). This the old dosage.';
comment on column substance_dosage.dosage_type is
'*=absolute, w=weight based (per kg body weight), s=surface based (per m2 body surface), a=age based (in months)';
comment on column substance_dosage.id_component is 'the component of a compound referred to by this row';
comment on column substance_dosage.dosage_start is
'lowest value of recommended dosage range';
comment on column substance_dosage.dosage_max is
'maximum value of recommended dosage range, zero if no range';


create table link_drug_class(
	id_drug integer references drug_element(id),
	id_class integer references drug_element(id)
);
create index idx_link_drug_class on link_drug_class(id_drug, id_class);
comment on table link_drug_class is
'A many-to-many pivot table linking classes to drugs';


create table link_drug_warning(
	id_drug integer references drug_element(id),
	id_warning integer references drug_warning(id)
);
create index idx_link_drug_warning on link_drug_warning(id_drug, id_warning);
comment on table link_drug_warning is
'A many-to-many pivot table linking warnings to drugs';


create table link_drug_information(
	id_drug integer references drug_element(id),
	id_info integer references drug_information(id)
);
create index idx_link_drug_information on link_drug_information(id_drug, id_info);
comment on table link_drug_information is
'A many-to-many pivot table linking product information to drugs';


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

-- some examples
insert into adverse_effects (severity, description) values (1, 'pruritis');
insert into adverse_effects (severity, description) values (1, 'nausea');
insert into adverse_effects (severity, description) values (1, 'postural hypotension');
insert into adverse_effects (severity, description) values (2, 'hepatitis');
insert into adverse_effects (severity, description) values (2, 'renal failure');
insert into adverse_effects (severity, description) values (2, 'ototoxicity');


create table link_drug_adverse_effects(
	id_drug integer references drug_element(id),
	id_adverse_effect integer references adverse_effects(id),
	frequency char check(frequency in ('c', 'i', 'r')),
	important boolean
);
comment on table link_drug_adverse_effects is
'many to many pivot table linking drugs to adverse effects';
comment on column link_drug_adverse_effects.frequency is
'The likelihood this adverse effect happens: c=common, i=infrequent, r=rare';
comment on column link_drug_adverse_effects.important is
'modifier for attribute "frequency" allowing to weigh rare adverse effects too important to miss';


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

insert into interactions (severity, description) values (1, 'increases half-life');
insert into interactions (severity, description) values (1, 'decreases half-life');
insert into interactions (severity, description) values (1, 'worsens disease');
insert into interactions (severity, description) values (1, 'unknown');
insert into interactions (severity, description) values (1, 'blocks receptor');


create table link_drug_interactions(
	id serial primary key,
	id_drug integer references drug_element(id),
	id_interacts_with integer references drug_element(id),
	id_interaction integer references interactions(id),
	comment text
);
comment on table link_drug_interactions is
'many to many pivot table linking drugs and their interactions';


create table link_drug_disease_interactions(
	id_drug integer references drug_element(id),
	id_code_system integer references code_systems(id),
	disease_code char(20),
	id_interaction integer references interactions(id),
	comment text
);
comment on table link_drug_disease_interactions is
'many to many pivot table linking interactions between drugs and diseases';


create table product(
	id serial primary key,
	id_generic_drug integer references drug_element(id),
	id_formulation integer references drug_formulations(id),
	packing_unit integer references drug_units(id),
	id_route integer references drug_routes (id),
	package_size float,
	comment text
);
comment on table product is
'dispensable form of a generic drug including strength, package size etc';
comment on column product.packing_unit is
'unit of drug "entities" as packed: for tablets and similar discrete formulations it should be the id of "each"';
comment on column product.package_size is
'the number of packing_units of this drug in this package';


create table link_product_component

(
	id_product integer references product (id),
	id_component integer references drug_element (id),
	strength float,
	id_unit integer references drug_units (id)
);

comment on table link_product_component  is 
'many-to-many pivot table linking products with their components';

create table drug_flags (
	id serial,
	description varchar (100)
);

comment on table drug_flags is 'flags for adjuvants such as ''gluten-free'', ''paediatric formulation'', etc.';

insert into drug_flags (description) values ('paediatric');
insert into drug_flags (description) values ('gluten-free');
insert into drug_flags (description) values ('slow-release');
insert into drug_flags (description) values ('enteric-coated');
insert into drug_flags (description) values ('flavoured');

create table link_flag_product (
	id_product integer references product (id),
	id_flag integer references drug_flags (id)
);

comment on table link_flag_product is 'many-to-many pivot table linking products to flags';


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
	comment text,
	code char (2)
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
comment on column manufacturer.code is
'two-letter symbol of manufacturer';


create table link_product_manufacturer(
	id_product integer references product(id),
	id_manufacturer integer references manufacturer(id),
	brandname varchar (60) default 'GENERIC'
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

create table conditions (
	id serial,
	comment text,
	authority boolean
);

comment on table conditions is 'normalised prescribing requirements for a drug or drugs';
comment on column conditions.authority is 'true if prescriber must contact the third-party before approval'; 

create table subsidized_products(
	id_product integer references product(id),
	id_subsidy integer references subsidies(id),
	max_qty integer default 1,
	max_rpt integer default 0,
	copayment float default 0.0,
	condition integer references conditions (id),
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


create table link_drug_indication(
	id serial primary key,
	id_drug integer references drug_element,
	id_code_system integer references code_systems,
	indication_code char(20),
	comment text,
	line integer
);

create index idx_drug_indication on link_drug_indication(id_drug);
create index idx_indication_drug on link_drug_indication(indication_code);
comment on table link_drug_indication is
'many to many pivot table linking drugs and indications';
comment on column link_drug_indication.indication_code is
'code of the disease/indication in the specified code system';
comment on column link_drug_indication.line is 'the line (first-line, second-line) of this drug for this indication'; 