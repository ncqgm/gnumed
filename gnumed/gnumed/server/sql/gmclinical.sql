-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmclinical.sql,v $
-- $Revision: 1.8 $
-- license: GPL
-- author: 

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- This database is internationalised!
-- run i18n.sql before running this script. 

create table audit_clinical (
	audit_id serial
);

comment on table audit_clinical is 
'ancestor table for auditing. Marks tables for automatic trigger generation';

create table enum_clinical_encounters(
	id SERIAL primary key,
	description text
)inherits (audit_clinical);


INSERT INTO enum_clinical_encounters (description)
	values (_('surgery consultation'));
INSERT INTO enum_clinical_encounters (description)
	values (_('phone consultation'));
INSERT INTO enum_clinical_encounters (description)
	values (_('fax consultation'));
INSERT INTO enum_clinical_encounters (description)
	values (_('home visit'));
INSERT INTO enum_clinical_encounters (description)
	values (_('nursing home visit'));
INSERT INTO enum_clinical_encounters (description)
	values (_('repeat script'));
INSERT INTO enum_clinical_encounters (description)
	values (_('hospital visit'));
INSERT INTO enum_clinical_encounters (description)
	values (_('video conference'));
INSERT INTO enum_clinical_encounters (description)
	values (_('proxy encounter'));
INSERT INTO enum_clinical_encounters (description)
	values (_('emergency encounter'));
INSERT INTO enum_clinical_encounters (description)
	values (_('other encounter'));

COMMENT ON TABLE enum_clinical_encounters is
'these are the types of encounter';


create table clinical_transaction(
	id SERIAL primary key,
	stamp timestamp with time zone,
	id_location int,
	id_doctor int,  
	id_patient int, 
	id_enum_clinical_encounters int REFERENCES enum_clinical_encounters (id)
) inherits (audit_clinical);

COMMENT ON TABLE clinical_transaction is
'unique identifier for clinical encounter';

COMMENT ON COLUMN clinical_transaction.stamp is 
'Date, time and timezone of the transaction.'; 

COMMENT ON COLUMN clinical_transaction.id_location is 
'Location ID, in ?? gmoffice';

COMMENT ON COLUMN clinical_transaction.id_doctor is 
'Doctor''s ID, in ?? gmoffice';

COMMENT ON COLUMN clinical_transaction.id_patient is 
'Patient''s ID, in gmidentity';

create table enum_clinical_history(
	id SERIAL primary key,
	description text
) inherits (audit_clinical);

COMMENT ON TABLE enum_clinical_history is
'types of history taken during a clinical encounter';


INSERT INTO enum_clinical_history (description)
	values (_('past'));
INSERT INTO enum_clinical_history (description)
	values (_('presenting complaint'));
INSERT INTO enum_clinical_history (description)
	values (_('history of present illness'));
INSERT INTO enum_clinical_history (description)
	values (_('social'));
INSERT INTO enum_clinical_history (description)
	values (_('family'));
INSERT INTO enum_clinical_history (description)
	values (_('immunisation'));
INSERT INTO enum_clinical_history (description)
	values (_('requests'));
INSERT INTO enum_clinical_history (description)
	values (_('allergy'));
INSERT INTO enum_clinical_history (description)
	values (_('drug'));
INSERT INTO enum_clinical_history (description)
	values (_('sexual'));
INSERT INTO enum_clinical_history (description)
	values (_('psychiatric'));
INSERT INTO enum_clinical_history (description)
	values (_('other'));

create table enum_info_sources
(
	id serial,
	description varchar (100)
);

comment on table enum_info_sources is
'sources of clinical information: patient, relative, notes, corresondence';

insert into enum_info_sources (description) values (_('patient'));
insert into enum_info_sources (description) values (_('clinician'));
insert into enum_info_sources (description) values (_('relative'));
insert into enum_info_sources (description) values (_('carer'));
insert into enum_info_sources (description) values (_('notes'));
insert into enum_info_sources (description) values (_('correspondence'));

create table clinical_history(
	id SERIAL primary key,
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


create table enum_coding_systems (
	id SERIAL primary key,
	description text
)inherits (audit_clinical);


COMMENT ON TABLE enum_coding_systems is
'The various types of coding systems available';

INSERT INTO enum_coding_systems (description)
	values (_('general'));
INSERT INTO enum_coding_systems (description)
	values (_('clinical'));
INSERT INTO enum_coding_systems (description)
	values (_('diagnosis'));
INSERT INTO enum_coding_systems (description)
	values (_('therapy'));
INSERT INTO enum_coding_systems (description)
	values (_('pathology'));
INSERT INTO enum_coding_systems (description)
	values (_('bureaucratic'));
INSERT INTO enum_coding_systems (description)
	values (_('ean'));
INSERT INTO enum_coding_systems (description)
	values (_('other'));


create table coding_systems (
	id SERIAL primary key,
	id_enum_coding_systems int REFERENCES enum_coding_systems (id),
	description text,
	version char(6),
	deprecated timestamp
)inherits (audit_clinical);

comment on table coding_systems is
'The coding systems in this database.';

create table clinical_diagnosis (
	id SERIAL primary key,
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

create table enum_confidentiality_level (
	id SERIAL primary key,
	description text
)inherits (audit_clinical);

comment on table enum_confidentiality_level is
'Various levels of confidentialoty of a coded diagnosis, such as public, clinical staff, treating doctor, etc.';

INSERT INTO enum_confidentiality_level (description)
	values (_('public'));
INSERT INTO enum_confidentiality_level (description)
	values (_('relatives'));
INSERT INTO enum_confidentiality_level (description)
	values (_('receptionist'));
INSERT INTO enum_confidentiality_level (description)
	values (_('clinical staff'));
INSERT INTO enum_confidentiality_level (description)
	values (_('doctors'));
INSERT INTO enum_confidentiality_level (description)
	values (_('doctors of practice only'));
INSERT INTO enum_confidentiality_level (description)
	values (_('treating doctor'));

create table clinical_diagnosis_extra (
	id SERIAL primary key,
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

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmclinical.sql,v $', '$Revision: 1.8 $');

-- =============================================
-- $Log: gmclinical.sql,v $
-- Revision 1.8  2002-12-06 08:50:51  ihaywood
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
