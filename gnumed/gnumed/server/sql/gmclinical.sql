-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmclinical.sql,v $
-- $Revision: 1.44 $
-- license: GPL
-- author: Ian Haywood, Horst Herb, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- clinical narrative aggregation, this is a generic table for SOAP
-- -------------------------------------------------------------------
create table clin_narrative (
	pk_narr serial primary key,
	narrative text
);

comment on table clin_narrative is
	'contains all the clinical narrative aggregated for full text search,
	 ancestor for all tables that want to store clinical free text';
comment on column clin_narrative.narrative is
	'well, the narrative itself';

-- ===================================================================
-- generic EMR structure
-- -------------------------------------------------------------------
create table clin_health_issue (
	id serial primary key,
	id_patient integer not null,
	description varchar(128) default '__default__',
	unique (id_patient, description)
) inherits (audit_mark);

comment on table clin_health_issue is
	'long-ranging, underlying health issue such as "mild immunodeficiency", "diabetes type 2"';
comment on column clin_health_issue.id_patient is
 	'id of patient this health issue relates to';
comment on column clin_health_issue.description is
	'descriptive name of this health issue, may change over time';

-- start: start of first episode
-- end: end of most recent episode

-- -------------------------------------------------------------------
create table clin_episode (
	id serial primary key,
	id_health_issue integer not null references clin_health_issue(id),
	description varchar(128) default '__default__',
	unique (id_health_issue, description)
) inherits (clin_narrative, audit_mark);

comment on table clin_episode is
	'clinical episodes such as "recurrent Otitis media", "traffic accident 7/99", "Hepatitis B"';
comment on column clin_episode.id_health_issue is
	'health issue this episode is part of';
comment on column clin_episode.description is
	'descriptive name of this episode, may change over time; if
	 "__default__" applications should display the most recently
	 associated diagnosis/month/year plus some marker for "default"';

-- unique names (descriptions) for episodes per health issue (e.g. per patient),
-- about the only reason for this table to exist is the description field such
-- as to allow arbitrary names for episodes, another reason is that explicit
-- recording of episodes removes the ambiguity that results from basing them
-- on start/end dates of bouts of care,

-- -------------------------------------------------------------------
create table _enum_encounter_type (
	id serial primary key,
	description varchar(32) unique not null
) inherits (audit_mark);

comment on TABLE _enum_encounter_type is
	'these are the types of encounter';

-- -------------------------------------------------------------------
create table clin_encounter (
	id serial primary key,
	id_location integer,
	id_provider integer,
	id_type integer not null references _enum_encounter_type(id)
) inherits (clin_narrative, audit_mark);

comment on table clin_encounter is
	'a clinical encounter between a person and the health care system';
comment on COLUMN clin_encounter.id_location is
	'ID of location *of care*, e.g. where the provider is at';
comment on COLUMN clin_encounter.id_provider is
	'ID of (main) provider of care';
comment on COLUMN clin_encounter.id_type is
	'ID of encounter type of this encounter';

-- about the only reason for this table to exist is the id_type
-- field, otherwiese one could just store the data in clin_item

-- ============================================
-- specific EMR content tables: SOAP++
-- --------------------------------------------
create table clin_item (
	pk_item serial primary key,
	id_encounter integer not null references clin_encounter(id),
	id_episode integer not null references clin_episode(id)
) inherits (clin_narrative);

comment on TABLE clin_item is
	'ancestor table for clinical items of any kind, can be used
	 directly for generic EMR entries';
comment on COLUMN clin_item.pk_item is
	'the primary key, not named "id" as usual since child tables
	 will have "id" primary keys already';
comment on COLUMN clin_item.id_encounter is
	'the encounter this item belongs to';
comment on COLUMN clin_item.id_episode is
	'the episode this item belongs to';

-- --------------------------------------------
create table _enum_hx_type (
	id serial primary key,
	description varchar(128) unique not null
);

comment on TABLE _enum_hx_type is
	'types of history taken during a clinical encounter';

-- --------------------------------------------
create table _enum_hx_source (
	id serial primary key,
	description varchar(128) unique not null
);

comment on table _enum_hx_source is
	'sources of clinical information: patient, relative, notes, correspondence';

-- --------------------------------------------
create table clin_history (
	id serial primary key,
	id_type integer not null references _enum_hx_type(id),
	id_source integer REFERENCES _enum_hx_source(id)
) inherits (clin_item, audit_mark);

-- narrative provided by clin_item

comment on TABLE clin_history is
	'narrative details of history taken during a clinical encounter';
comment on COLUMN clin_history.id_type is
	'the type of history taken';
comment on COLUMN clin_history.id_source is
	'who provided the details of this entry';

-- --------------------------------------------
create table clin_physical (
	id serial primary key
) inherits (clin_item, audit_mark);

-- narrative provided by clin_item

comment on TABLE clin_physical is
	'narrative details of physical exam during a clinical encounter';

-- --------------------------------------------
create table _enum_allergy_type (
	id serial primary key,
	value varchar(32) unique not null
) ;

-- --------------------------------------------
create table allergy (
	id serial primary key,
	substance varchar(128) not null,
	substance_code varchar(256) default null,
	generics varchar(256) default null,
	allergene varchar(256) default null,
	atc_code varchar(32) default null,
	id_type integer not null references _enum_allergy_type(id),
	reaction text default '',
	generic_specific boolean default false,
	definate boolean default false
) inherits (clin_item, audit_mark);

-- narrative provided by clin_item

comment on table allergy is
	'patient allergy details';
comment on column allergy.substance is
	'real-world name of substance the patient reacted to, brand name if drug';
comment on column allergy.substance_code is
	'data source specific opaque product code; must provide a link
	 to a unique product/substance in the database in use; should follow
	 the parseable convention of "<source>::<source version>::<identifier>",
	 e.g. "MIMS::2003-1::190" for Zantac; it is left as an exercise to the
	 application to know what to do with this information';
comment on column allergy.generics is
	'names of generic compounds if drug; brand names change/disappear, generic names do not';
comment on column allergy.allergene is
	'name of allergenic ingredient in substance if known';
comment on column allergy.atc_code is
	'ATC code of allergene or substance if approprate, applicable for penicilline, not so for cat fur';
comment on column allergy.id_type is
	'allergy/sensitivity';
comment on column allergy.reaction is
	'description of reaction such as "difficulty breathing, "skin rash", "diarrhea" etc.';
comment on column allergy.generic_specific is
	'true: only applies to the generic named in allergene, false: applies to class the substance in allergene belongs to; if substance in allergene is not found in generics (eg. it is something else), then generic_specific has no meaning)';
comment on column allergy.definate is
	'true: definate, false: not definate';

-- ===================================================================
-- following tables not yet converted to EMR structure ...
-- -------------------------------------------------------------------
create table enum_coding_systems (
	id serial primary key,
	description text
) inherits (audit_mark);

comment on TABLE enum_coding_systems is
	'The various types of coding systems available';

-- -------------------------------------------------------------------
create table coding_systems (
	id serial primary key,
	id_enum_coding_systems int REFERENCES enum_coding_systems (id),
	description text,
	version char(6),
	deprecated timestamp
) inherits (audit_mark);

comment on table coding_systems is
	'The coding systems in this database.';

-- -------------------------------------------------------------------
create table clin_diagnosis (
	id serial primary key,
	approximate_start text DEFAULT null,
	code char(16),
	id_coding_systems int REFERENCES coding_systems (id),
	text text
) inherits (audit_mark);

comment on TABLE clin_diagnosis is
	'Coded clinical diagnoses assigned to patient, in addition to history';
comment on column clin_diagnosis.approximate_start is
	'around the time at which this diagnosis was made';
comment on column clin_diagnosis.code is
	'the code';
comment on column clin_diagnosis.id_coding_systems is
	'the coding system used to code the diagnosis';
comment on column clin_diagnosis.text is
	'extra notes on the diagnosis';

-- -------------------------------------------------------------------
create table enum_confidentiality_level (
	id SERIAL primary key,
	description text
)inherits (audit_mark);

comment on table enum_confidentiality_level is
	'Various levels of confidentialoty of a coded diagnosis, such as public, clinical staff, treating doctor, etc.';

-- -------------------------------------------------------------------
create table clin_diagnosis_extra (
	id serial primary key,
	id_clin_diagnosis int REFERENCES clin_diagnosis (id),
	id_enum_confidentiality_level int REFERENCES enum_confidentiality_level (id)
) inherits (audit_mark);

comment on table clin_diagnosis_extra is
'Extra information about a diagnosis, just the confidentiality level at present.';

-- ============================================
-- Drug related tables

-- These tables are pasted from gmdrugs.sql, how do we otherwise
-- deal with this?

create table drug_units (
	id serial primary key,
	unit varchar(30)
);
comment on table drug_units is
'(SI) units used to quantify/measure drugs';
comment on column drug_units.unit is
'(SI) units used to quantify/measure drugs like "mg", "ml"';


create table drug_formulations(
	id serial primary key,
	description varchar(60),
	comment text
);
comment on table drug_formulations is
'presentations or formulations of drugs like "tablet", "capsule" ...';
comment on column drug_formulations.description is
'the formulation of the drug, such as "tablet", "cream", "suspension"';


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

create table script_drug
(
	id serial primary key,
	brandname varchar (200) default 'GENERIC',
	directions text,
	adjuvant text,
	db_xref varchar (128) not null,
	atc_code varchar (32),
	total_amount float,
	dose_amount float,
	amount_unit integer references drug_units (id),
	packsize integer,
	id_route integer references drug_routes (id) not null,
	id_form integer references drug_formulations (id) not null,
	prn boolean,
	frequency integer not null
);

comment on table script_drug is
'table for different prescriptions. Note the multiple redundancy of the stored drug data.
Applications should try in this order:
- internal database code
- brandname
- ATC code
- generic name(s) (in constituents)
';
--comment on column script_drug.xref_id is 'ID of the source database';
comment on column script_drug.total_amount is 'the total amount to be dispensed';
comment on column script_drug.dose_amount is 'the amount to be consumed at each dose';
comment on column script_drug.prn is 'true if "pro re nata" (= as required)';
comment on column script_drug.directions is 'free text for directions, such as ''nocte'' etc';
comment on column script_drug.adjuvant is 'free text describing adjuvants, such as ''orange-flavoured'' etc.';
	
create table constituents
(
	id serial primary key,
	genericname varchar (100),
	dose float,
	dose_unit integer references drug_units (id),
	id_drug integer references script_drug (id)
);

comment on table constituents is
'the constituent substances of the various drugs (normalised out to support compound drugs like Augmentin)';
--comment on column constituents.name is
--'the English IUPHARM standard name, as a base, with no adjuvant, in capitals. So MORPHINE. not Morphine, not MORPHINE SULPHATE, not MORPHINIUM';
comment on column constituents.dose is
'the amount of drug (if salt, the amount of active base substance, in a unit (see amount_unit above)';
 
create table script
(
	id serial primary key
);

comment on table script is
'one row for each physical prescription printed. Can have multiple drugs on a script, 
and multiple scripts in a transaction';

create table link_script_drug
(
	id_drug integer references script_drug (id),
	id_script integer references script (id),
	comment text
);

comment on table link_script_drug is
'many-to-many table for drugs and prescriptions';

-- =============================================

create table enum_immunities
(
	id serial primary key,
	name text
);

comment on table enum_immunities is
'list of diseases to which patients may have immunity. Same table must exist in gmdrugs';

-- =============================================
GRANT SELECT ON
	"clin_narrative",
	"clin_health_issue",
	"clin_episode",
	"_enum_encounter_type",
	"clin_encounter",
	"clin_item",
	"_enum_hx_type",
	"_enum_hx_source",
	"clin_history",
	"clin_physical",
	"_enum_allergy_type",
	"allergy"
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	"clin_narrative",
	"clin_narrative_pk_narr_seq",
	"clin_health_issue",
	"clin_health_issue_id_seq",
	"clin_episode",
	"clin_episode_id_seq",
	"_enum_encounter_type",
	"_enum_encounter_type_id_seq",
	"clin_encounter",
	"clin_encounter_id_seq",
	"clin_item",
	"clin_item_pk_item_seq",
	"_enum_hx_type",
	"_enum_hx_type_id_seq",
	"_enum_hx_source",
	"_enum_hx_source_id_seq",
	"clin_history",
	"clin_history_id_seq",
	"clin_physical",
	"clin_physical_id_seq",
	"_enum_allergy_type",
	"_enum_allergy_type_id_seq",
	"allergy",
	"allergy_id_seq"
TO GROUP "_gm-doctors";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmclinical.sql,v $', '$Revision: 1.44 $');

-- =============================================
-- $Log: gmclinical.sql,v $
-- Revision 1.44  2003-05-12 19:29:45  ncq
-- - first stab at real auditing
--
-- Revision 1.43  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.42  2003/05/06 13:06:25  ncq
-- - pkey_ -> pk_
--
-- Revision 1.41  2003/05/05 12:40:03  ncq
-- - name is not a field of constituents anymore
--
-- Revision 1.40  2003/05/05 12:26:31  ncq
-- - remove comment on xref_id in script_drug, xref_id does not exist
--
-- Revision 1.39  2003/05/05 11:58:51  ncq
-- - audit_clinical -> clin_audit + use it
-- - clin_narrative now ancestor table + use it (as discussed with Ian)
--
-- Revision 1.38  2003/05/05 10:02:10  ihaywood
-- minor updates
--
-- Revision 1.37  2003/05/04 23:35:59  ncq
-- - major reworking to follow the formal EMR structure writeup
--
-- Revision 1.36  2003/05/03 00:44:40  ncq
-- - remove had_hypo from allergies table
--
-- Revision 1.35  2003/05/02 15:08:55  ncq
-- - episodes must have unique names (==description) per health issue
-- - remove cruft
-- - add not null to id_type in clin_encounter
-- - default id_comment in allergy to null
--
-- Revision 1.34  2003/05/01 15:06:29  ncq
-- - allergy.id_substance -> allergy.substance_code
--
-- Revision 1.33  2003/04/30 23:30:29  ncq
-- - v_i18n_patient_allergies
-- - new_allergy -> allergy_new
--
-- Revision 1.32  2003/04/29 12:38:32  ncq
-- - add not null to referencing constraints in episode/transactions
--
-- Revision 1.31  2003/04/28 21:40:40  ncq
-- - better indices
--
-- Revision 1.30  2003/04/28 20:56:16  ncq
-- - unclash "allergy" in hx type and type of allergic reaction + translations
-- - some useful indices
--
-- Revision 1.29  2003/04/25 12:43:52  ncq
-- - add grants
--
-- Revision 1.28  2003/04/25 12:32:39  ncq
-- - view on encounter types needs "as description"
--
-- Revision 1.27  2003/04/18 13:30:35  ncq
-- - add doc types
-- - update comment on allergy.id_substance
--
-- Revision 1.26  2003/04/17 20:20:11  ncq
-- - add source specific opaque substance/product identifier in table allergy
--
-- Revision 1.25  2003/04/12 15:34:49  ncq
-- - include the concept of aggregated clinical narrative
-- - consolidate history/physical exam tables
--
-- Revision 1.24  2003/04/09 14:47:17  ncq
-- - further tweaks on allergies tables
--
-- Revision 1.23  2003/04/09 13:50:29  ncq
-- - typos
--
-- Revision 1.22  2003/04/09 13:10:13  ncq
-- - _clinical_ -> _clin_
-- - streamlined episode/encounter/transaction
--
-- Revision 1.21  2003/04/07 12:28:24  ncq
-- - allergies table updated according to comments on resmed-de and gm-dev
--
-- Revision 1.20  2003/04/06 15:18:21  ncq
-- - can't reference _()ed fields in a view since it can't find the unique constraint in the underlying table
--
-- Revision 1.19  2003/04/06 15:10:05  ncq
-- - added some missing unique constraints
--
-- Revision 1.18  2003/04/06 14:51:40  ncq
-- - more cleanly separated data and schema
-- - first draft of allergies table
--
-- Revision 1.17  2003/04/02 13:37:56  ncq
-- - fixed a few more missing "primary key" on referenced "id serial"s
--
-- Revision 1.16  2003/04/02 12:31:07  ncq
-- - PostgreSQL 7.3 complained about referenced key enum_info_sources.id not being unique()d
-- -> make it primary key as it should be
--
-- Revision 1.15  2003/03/27 21:14:49  ncq
-- - cleanup, started work on Dutch structure
--
-- Revision 1.14  2003/01/20 20:10:12  ncq
-- - adapted to new i18n
--
-- Revision 1.13  2003/01/13 10:07:52  ihaywood
-- add free comment strings to script.
-- Start vaccination Hx tables
--
-- Revision 1.12  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.11  2002/12/22 01:26:16  ncq
-- - id_doctor -> id_provider + comment, typo fix
--
-- Revision 1.10  2002/12/14 08:55:17  ihaywood
-- new prescription tables -- fixed typos
--
-- Revision 1.9  2002/12/14 08:12:22  ihaywood
-- New prescription tables in gmclinical.sql
--
-- Revision 1.8  2002/12/06 08:50:51  ihaywood
-- SQL internationalisation, gmclinical.sql now internationalised.
--
-- Revision 1.7  2002/12/05 12:45:43  ncq
-- - added episode table, fixed typo
--
-- Revision 1.6  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.5  2002/11/23 13:18:09  ncq
-- - add "proper" metadata handling and schema revision tracking
--
