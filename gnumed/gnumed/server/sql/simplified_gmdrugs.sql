-- DDL structure of drug database for the gnumed project
-- Copyright 2000, 2001, 2002 by Horst Herb, Ian Haywood, Karsten Hilbert
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- This is a simplifying rewrite since the December 2002 version
-- It aims at reducing complexity and improving performance
--
-- usage:
--	log into psql (database gnumed OR drugs)  as administrator
--	run the script from the prompt with "\i drugs.sql"
--=====================================================================

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/simplified_gmdrugs.sql,v $
-- $Revision: 1.2 $ $Date: 2003-01-01 14:10:00 $ $Author: hherb $
-- ============================================================

\set ON_ERROR_STOP 1

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

-- couple of examples
insert into info_reference (source_category, description) values ('i', 'Rang, Dale, and Ritter <i>Pharmacology</i>, 1999');

create table code_systems(
	id serial primary key,
	iso_countrycode char(2) default '**',
	name varchar(30),
	version varchar(30),
	revision varchar(30)
);
comment on table code_systems is
'listing of disease coding systems used for drug indication listing';
comment on column code_systems.iso_countrycode is
'ISO country code of country where this code system applies. Use "**" for wildcard';
comment on column code_systems.name is
'name of the code systme like ICD, ICPC';
comment on column code_systems.version is
'version of the code system, like "10" for ICD-10';
comment on column code_systems.revision is
'revision of the version of the coding system/classification';

insert into code_systems(name, version, revision) values ('ICD', '10', 'SGBV v1.3');
insert into code_systems(name, version) values ('ICPC', '2');


create table problem (
	id serial primary key,
	id_code_system integer references code_systems(id),
	code varchar(20),
	description text
);

comment on table problem is
'coded medical condition, disease or problem as used for indications, contraindications and interactions';
comment on column problem.code is
'the original code as taking from the referenced coding system';
comment on column problem.description is
'optional verbose description of the problem';


create table ATC (
	code char(8) primary key,
	description text
);

comment on table ATC is
'ATC code (http://www.whocc.no/atcddd/)';


create table drug (
	id serial primary key,
	ATC char(8),
	compound boolean default 'f',
	INN varchar(255)
);

comment on table drug is
'a drug may consist of either a single or multiple active ingredients';

comment on column drug.ATC is
'ATC code (http://www.whocc.no/atcddd/)';

comment on column drug.compound is
'"t" if this drug consist of multiple active ingredients, else "f"';

comment on column drug.INN is
'international non-proprietary name = generic name. Other names see table names_drug';



create table drug_components (
	id_drug integer references drug(id),
	id_component integer references drug(id)
);

comment on table drug_components is
'many-2-many pivot table linking components of a compound drug.';

comment on column drug_components.id_drug is
'id of the dominant component, or of the alphabetically first on if there is no dominant component';

comment on column drug_components.id_component is
'id of a component of ths drug';



create table names_drug(
	country char(2),
	id_drug integer references drug(id),
	name varchar(255)
);

comment on table names_drug is
'allows to allocate country specific synonyms to a drug name';

comment on column names_drug.country is
'Two character ISO country code';


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
insert into drug_units(unit) values('mg/g');
insert into drug_units(unit) values('U');
insert into drug_units(unit) values('IU');
insert into drug_units(unit) values('each');
insert into drug_units(unit) values('mcg');
insert into drug_units(unit) values('mcg/ml');
insert into drug_units(unit) values('IU/ml');


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
insert into drug_formulations(description) values ('kit');


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


create table warning(
	id serial primary key,
	id_warning integer references drug_warning_categories(id),
	id_reference integer references info_reference(id) default NULL,
	code char(4),
	details text
);
comment on table warning is
'any warning associated with a specific drug';
comment on column warning.code is
'severity of the warning (like the the A,B,C,D scheme for pregnancy related warnings)';
comment on column warning.code is
'could have been implemented as foreign key to a table of severity codes, but was considered uneccessary';


create table drug_warning (
	id_drug integer references drug(id),
	id_warning integer references warning(id)
);

comment on table drug_warning is
'pivot table associating drugs with any number of warnings';



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
	id_drug integer references drug(id),
	id_info_reference integer references info_reference(id),
	info text,
	id_topic integer references information_topic (id),
	comment text
);
comment on table drug_information is
'any product information about a specific drug in HTML format';
comment on column drug_information.info is
'the drug product information in HTML format';


create table dosage_suggestion(
	id serial primary key,
	id_drug integer references drug(id),
	id_route integer references drug_routes (id),
	id_unit integer references drug_units (id),
	id_reference integer references info_reference(id),
	dosage_type char check (dosage_type in ('*', 'w', 's', 'a')),
	dosage_start float,
	dosage_max float,
	hints text
);

comment on table dosage_suggestion is
'Dosage suggestion for a particular drug';
comment on column dosage_suggestion.dosage_type is
'*=absolute, w=weight based (per kg body weight), s=surface based (per m2 body surface), a=age based (in months)';
comment on column dosage_suggestion.dosage_start is
'lowest value of recommended dosage range';
comment on column dosage_suggestion.dosage_max is
'maximum value of recommended dosage range, zero if no range';
comment on column dosage_suggestion.hints is
'free text warnings, tips & hints regarding applying this dosage recommendation';


create table severity_level
(
	id serial,
	description varchar (100)
);

insert into severity_level values (0, 'irrelevant');
insert into severity_level values (1, 'trivial');
insert into severity_level values (2, 'minor');
insert into severity_level values (3, 'major');
insert into severity_level values (4, 'critical');



create table adverse_effects(
	id serial primary key,
	severity integer references severity_level (id),
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
insert into adverse_effects (severity, description) values (2, 'postural hypotension');
insert into adverse_effects (severity, description) values (2, 'drowsiness');
insert into adverse_effects (severity, description) values (2, 'tremor');
insert into adverse_effects (severity, description) values (3, 'hepatitis');
insert into adverse_effects (severity, description) values (3, 'renal failure');
insert into adverse_effects (severity, description) values (3, 'ototoxicity');
insert into adverse_effects (severity, description) values (3, 'confusion');
insert into adverse_effects (severity, description) values (3, 'psychosis');
insert into adverse_effects (severity, description) values (3, 'ototoxicity');



create table drug_adverse_effects(
	id_drug integer references drug(id),
	id_adverse_effect integer references adverse_effects(id),
	id_reference integer references info_reference(id),
	frequency char check(frequency in ('c', 'i', 'r')),
	important boolean,
	comment text
);
comment on table drug_adverse_effects is
'many to many pivot table linking drugs to adverse effects';
comment on column drug_adverse_effects.frequency is
'The likelihood this adverse effect happens: c=common, i=infrequent, r=rare';
comment on column drug_adverse_effects.important is
'modifier for attribute "frequency" allowing to weigh rare adverse effects too important to miss';



create table interactions(
	id serial primary key,
	severity integer references severity_level (id),
	id_reference integer references info_reference(id),
	description text,
	comment text
);
comment on table interactions is
'possible interactions between drugs';
comment on column interactions.severity is
'severity/significance of a potential interaction: the scale has yet to be agreed upon';
comment on column interactions.description is
'the type of interaction (like: "increases half life")';

insert into interactions (severity, description) values (1, 'unknown');
insert into interactions (severity, description) values (1, 'increases half-life');
insert into interactions (severity, description) values (1, 'decreases half-life');
insert into interactions (severity, description) values (1, 'worsens disease');
insert into interactions (severity, description) values (1, 'blocks receptor');


create table drug_drug_interactions(
	id serial primary key,
	id_drug integer references drug(id),
	id_interacts_with integer references drug(id),
	id_interaction integer references interactions(id),
	id_reference integer references info_reference(id),
	multiple boolean default 'f',
	comment text
);
comment on table drug_drug_interactions is
'many to many pivot table linking drugs and their interactions';

comment on column drug_drug_interactions.multiple is
'true ("t") if this describes a many-to-many drug interaction, see table multiple_drug_interactions';


create table multiple_drug_interactions(
	id_drug_drug_interactions integer references drug_drug_interactions(id),
	id_other_drug integer references drug(id),
	id_reference integer references info_reference(id),
	comment text
);

comment on table multiple_drug_interactions is
'extends drug-drug interactions in that any numbr of drugs can be linked into an interaction that way';

comment on column multiple_drug_interactions.id_other_drug is
'"other drug" required in an interaction with more than two drugs interacting. The two most significant drugs in this interaction should be listed in the referenced interaction';



create table drug_disease_interactions(
	id serial,
	id_drug integer references drug(id),
	id_problem integer references problem(id),
	id_interaction integer references interactions (id),
	comment text
);
comment on table drug_disease_interactions is
'many to many pivot table linking interactions between drugs and diseases';


