-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmclinical.sql,v $
-- $Revision: 1.18 $
-- license: GPL
-- author: Ian Haywood, Horst Herb

-- ===================================================================
-- This database is internationalised!

-- do fixed string i18n()ing
\i gmI18N.sql

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table audit_clinical (
	audit_id serial
);

comment on table audit_clinical is 
'ancestor table for auditing. Marks tables for automatic trigger generation';

-- -------------------------------------------------------------------
create table enum_clinical_encounters(
	id serial primary key,
	description text
)inherits (audit_clinical);

COMMENT ON TABLE enum_clinical_encounters is
'these are the types of encounter';

-- -------------------------------------------------------------------
create table clinical_encounter (
	id serial primary key
) inherits (audit_clinical);

-- -------------------------------------------------------------------
create table clinical_transaction (
	id serial primary key,
	id_location int,
	id_provider int,
	id_patient int,
	id_enum_clinical_encounters int REFERENCES enum_clinical_encounters (id),
	stamp timestamp with time zone,
	duration interval
) inherits (audit_clinical);

COMMENT ON TABLE clinical_transaction is
	'unique identifier for clinical transaction';

COMMENT ON COLUMN clinical_transaction.stamp is 
	'Date, time and timezone of the transaction.'; 

COMMENT ON COLUMN clinical_transaction.id_location is 
	'Location ID, in ?? gmoffice';

COMMENT ON COLUMN clinical_transaction.id_provider is 
	'ID of doctor/nurse/patient/..., in ?? gmoffice';

COMMENT ON COLUMN clinical_transaction.id_patient is 
	'Patient''s ID, in gmidentity';

-- -------------------------------------------------------------------
create table enum_clinical_history(
	id serial primary key,
	description text
) inherits (audit_clinical);

COMMENT ON TABLE enum_clinical_history is
'types of history taken during a clinical encounter';

-- -------------------------------------------------------------------
create table enum_info_sources
(
	id serial primary key,
	description varchar (100)
);

comment on table enum_info_sources is
'sources of clinical information: patient, relative, notes, correspondence';

-- -------------------------------------------------------------------
create table clinical_history(
	id serial primary key,
	id_enum_clinical_history int REFERENCES enum_clinical_history (id),
	id_clinical_transaction int  REFERENCES clinical_transaction (id),
	id_info_sources int REFERENCES enum_info_sources (id),
	text text
)inherits (audit_clinical);

COMMENT ON TABLE clinical_history is
'narrative details of history taken during a clinical encounter';

COMMENT ON COLUMN clinical_history.id_enum_clinical_history is
'the type of history taken';

COMMENT ON COLUMN clinical_history.id_clinical_transaction is
'The transaction during which this history was taken';

COMMENT ON COLUMN clinical_history.text is
'The text typed by the doctor';

-- -------------------------------------------------------------------
create table enum_coding_systems (
	id serial primary key,
	description text
)inherits (audit_clinical);


COMMENT ON TABLE enum_coding_systems is
'The various types of coding systems available';

-- -------------------------------------------------------------------
create table coding_systems (
	id serial primary key,
	id_enum_coding_systems int REFERENCES enum_coding_systems (id),
	description text,
	version char(6),
	deprecated timestamp
)inherits (audit_clinical);

comment on table coding_systems is
'The coding systems in this database.';

-- -------------------------------------------------------------------
create table clinical_diagnosis (
	id serial primary key,
	id_clinical_transaction int  REFERENCES clinical_transaction (id),
	approximate_start text DEFAULT null,
	code char(16),
	id_coding_systems int REFERENCES coding_systems (id),
	text text
)inherits (audit_clinical);

COMMENT ON TABLE clinical_diagnosis is
'Coded clinical diagnoses assigned to patient, in addition to history';

comment on column clinical_diagnosis.id_clinical_transaction is
'the transaction in which this diagnosis was made.';

comment on column clinical_diagnosis.approximate_start is
'around the time at which this diagnosis was made';

comment on column clinical_diagnosis.code is
'the code';
comment on column clinical_diagnosis.id_coding_systems is
'the coding system used to code the diagnosis';

comment on column clinical_diagnosis.text is
'extra notes on the diagnosis';

-- -------------------------------------------------------------------
create table enum_confidentiality_level (
	id SERIAL primary key,
	description text
)inherits (audit_clinical);

comment on table enum_confidentiality_level is
'Various levels of confidentialoty of a coded diagnosis, such as public, clinical staff, treating doctor, etc.';

-- -------------------------------------------------------------------
create table clinical_diagnosis_extra (
	id serial primary key,
	id_clinical_diagnosis int REFERENCES clinical_diagnosis (id),
	id_enum_confidentiality_level int REFERENCES enum_confidentiality_level (id)

)inherits (audit_clinical);

comment on table clinical_diagnosis_extra is
'Extra information about a diagnosis, just the confidentiality level at present.';

-- =============================================
-- episode related tables
create table episode (
	id serial primary key,
	id_patient integer not null,
	name varchar(128) default 'unspecified'
) inherits (audit_clinical);

comment on table episode is
	'clinical episodes such as "recurrent Otitis media", "traffic accident 7/99", "Hepatitis B"';
comment on column episode.id_patient is
	'id of patient this episode relates to';
comment on column episode.name is
	'descriptive name of this episode, may change over time';

-- ============================================
create table _enum_allergy_certainty (
	id serial primary key,
	value varchar(32)
) ;

create view vi18n_enum_allergy_certainty as
	select _enum_allergy_certainty.id, _(_enum_allergy_certainty.value)
	from _enum_allergy_certainty;

-- --------------------------------------------
create table _enum_allergy_type (
	id serial primary key,
	value varchar(32)
) ;

create view vi18n_enum_allergy_type as
	select _enum_allergy_type.id, _(_enum_allergy_type.value)
	from _enum_allergy_type;

-- --------------------------------------------
-- IMHO this is non-episode-related data
create table allergy (
	id serial primary key,
	id_clinical_transaction integer references clinical_transaction(id),
	substance varchar(128) not null,
	allergene varchar(256) default null,
	description text,
	certainty varchar(32) references vi18n_enum_allergy_certainty(name),
	type varchar(32) references vi18n_enum_allergy_type(name),
	first_observed varchar(32),
	code varchar(32)
) inherits (audit_clinical);

comment on table allergy is
	'patient allergy details';
comment on column allergy.id_clinical_transaction is
	'link to transaction, provides: patient, recorded_when';
comment on column allergy.substance is
	'real-world name of substance the patient reacted to';
comment on column allergy.allergene is
	'name of allergenic ingredient in substance if known';
comment on column allergy.description is
	'free-text description of reaction such as "difficulty breathing, "skin rash", "diarrhea" etc.';
comment on column allergy.certainty is
	'definate/likely';
comment on column allergy.type is
	'allergy/sensitivity';
comment on column allergy.first_observed is
	'this has been observed when for the first time, if known';
comment on column allergy.code is
	'ATC code of allergene or subtance if approprate, applicable for penicilline, not so for cat fur';

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

create table databases
(
	id serial primary key,
	name varchar (50),
	published date
);

comment on table databases is
'different drug databases';


create table script_drug
(
	id serial primary key,
	name varchar (200) default 'GENERIC',
	directions text,
	adjuvant text,
	xref_id varchar (100),
	source integer references databases (id),
	fluid_amount float,
	amount_unit integer references drug_units (id),
	amount integer,
	id_route integer references drug_routes (id),
	id_form integer references drug_formulations (id),
	prn boolean,
	frequency integer
);

comment on table script_drug is
'table for different prexcriptions';
comment on column script_drug.xref_id is 'ID of the source database';
comment on column script_drug.fluid_amount is 'if a fluid, the amount in each bottle/ampoule, etc.';
comment on column script_drug.amount is 'for solid object (tablets, capsules) the number of objects, for fluids, the number of separate containers';
comment on column script_drug.prn is 'true if "pro re nata" (= as required)';
comment on column script_drug.directions is 'free text for directions, such as ''nocte'' etc';
comment on column script_drug.adjuvant is 'free text describing adjuvants, such as ''orange-flavoured'' etc.';
	
create table constituents
(
	id serial primary key,
	name varchar (100),
	dose float,
	dose_unit integer references drug_units (id),
	id_drug integer references script_drug (id)
);

comment on table constituents is
'the constituent substances of the various drugs';
comment on column constituents.name is
'the English IUPHARM standard name, as a base, with no adjuvant, in capitals. So MORPHINE. not Morphine, not MORPHINE SULPHATE, not MORPHINIUM';
comment on column constituents.dose is
'the amount of drug (if salt, the amount of active base substance, in a unit (see amount_unit above)';
 
create table script
(
	id serial primary key,
	id_transaction integer references clinical_transaction (id)
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
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmclinical.sql,v $', '$Revision: 1.18 $');

-- =============================================
-- $Log: gmclinical.sql,v $
-- Revision 1.18  2003-04-06 14:51:40  ncq
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
