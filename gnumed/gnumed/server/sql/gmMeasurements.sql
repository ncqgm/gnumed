-- GnuMed - test/measurement related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- author: Christof Meigen <christof@nicht-ich.de>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmMeasurements.sql,v $
-- $Revision: 1.4 $

-- this belongs into the service clinical (historica)

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
create table practice_dummy (
	id serial primary key,
	dummy varchar(10)
);

-- ====================================
create table test_org (
	id serial primary key,
	id_practice integer unique not null references practice_dummy(id),
	id_adm_contact integer default null,
	id_med_contact integer default null,
	"comment" text
) inherits (audit_mark, audit_fields);

-- remote foreign keys
insert into x_db_fk (fk_table, fk_col, src_service, src_table, src_col)
	values ('test_org', 'id_adm_contact', 'personalia', 'identity', 'id');
insert into x_db_fk (fk_table, fk_col, src_service, src_table, src_col)
	values ('test_org', 'id_med_contact', 'personalia', 'identity', 'id');

COMMENT ON TABLE test_org IS
	'organisation providing results';
COMMENT ON COLUMN test_org.id_practice IS
	'address or organisation';
COMMENT ON COLUMN test_org.id_adm_contact IS
	'whom to call for admin questions (modem link, etc.)';
COMMENT ON COLUMN test_org.id_med_contact IS
	'whom to call for medical questions (result verification,
	 additional test requests)';
comment on column test_org."comment" is
	'useful for, say, dummy records where you want
	 to mark up stuff like "pharmacy such-and-such"
	 if you don''t have it in your contacts';

-- there need to be two pseudo org records
--  1) your own practice
--  2) "non-medical person" (exactly *who* may be in *_result)

create table log_test_org (
	id integer not null,
	id_practice integer not null,
	id_adm_contact integer,
	id_med_contact integer,
	"comment" text
) inherits (audit_trail);

-- ====================================
create table test_type (
	id serial primary key,
	id_provider integer references test_org,
	code text not null,
	coding_system text default null,
	"name" text,
	"comment" text,
	unique (id_provider, code)
) inherits (audit_mark, audit_fields);

-- remote foreign keys
insert into x_db_fk (fk_table, fk_col, src_service, src_table, src_col)
	values ('test_type', 'coding_system', 'reference', 'ref_source', 'name_short');
-- column "code" would have to be checked, too, but we don't
-- know against which table in "reference" since that depends
-- on "coding_system" ...

comment on table test_type is
	'measurement type, like a "method" in a lab';
comment on column test_type.id_provider is
	'organisation carrying out this type of measurement, eg. a particular lab';
comment on column test_type.code is
	'short name, acronym or code of this type of measurement,
	 may conform to some official list or other such as LOINC,
	 Australian Pathology request codes or German lab-specific ELVs';
comment on column test_type.coding_system is
	'identifier of coding system that the code of this
	 measurement type is taken from, should be verifiable
	 against the "reference" service of GnuMed';
comment on column test_type."name" is
	'descriptive name of this measurement type';
comment on column test_type."comment" is
	'arbitrary comment on this type of measurement/test such
	 as "outdated" or "only reliable when ..."';

create table log_test_type (
	id integer not null,
	id_provider integer not null,
	code text not null,
	coding_system text,
	"name" text,
	"comment" text
) inherits (audit_trail);

-- ====================================
create table test_result (
	id serial primary key,
	id_type integer references test_type,

	val_when timestamp with time zone not null default CURRENT_TIMESTAMP,
	val_num float,
	val_alpha text,
	val_unit text,
	val_normal_min float,
	val_normal_max float,
	val_normal_range text,
	technically_abnormal bool not null,
	note_provider text,

	reviewed_by_clinician bool default false,
	id_clinician integer,
	clinically_relevant bool
) inherits (audit_mark, clin_root_item);

-- note_clinician provided as narrative by clin_root_item

-- remote foreign keys
insert into x_db_fk (fk_table, fk_col, src_service, src_table, src_col)
	values ('test_result', 'val_unit', 'reference', 'unit', 'name_short');

COMMENT ON TABLE test_result is 
	'the results of a single measurement';
comment on column test_result.id_type is
	'the type of test this result is from';
comment on column test_result.val_when is
	'the timestamp when the result was actually produced';
comment on column test_result.val_num is
	'numeric value if any';
comment on column test_result.val_alpha is
	'alphanumeric value if any';
comment on column test_result.val_unit is
	'the unit this result came in';
comment on column test_result.val_normal_min is
	'lower bound of normal range if numerical as
	 defined by provider for this result';
comment on column test_result.val_normal_max is
	'upper bound of normal range if numerical as
	 defined by provider for this result';
comment on column test_result.val_normal_range is
	'range of normal values if alphanumerical
	 as defined by provider for this result, eg.
	 "less than 0.5 but detectable"';
comment on column test_result.technically_abnormal is
	'whether provider flagged this result as abnormal,
	 *not* a clinical assessment but rather a technical one';
comment on column test_result.note_provider is
	'any comment the provider should like to make, such
	 as "may be inaccurate due to lack of adequate sample"';
comment on column test_result.reviewed_by_clinician is
	'whether a clinician has seen this result yet,
	 depending on the use case this need to simply get
	 set by any read access but may follow specific
	 business rules such as "set as SEEN when treating/
	 requesting doctor has reviewed the item"';
comment on column test_result.id_clinician is
	'who has reviewed the item';
comment on column test_result.clinically_relevant is
	'whether this result is considered relevant clinically,
	 need not correspond to the value of "techically_abnormal"
	 since abnormal values may be irrelevant while normal
	 ones can be of significance';

create table log_test_result (
	id integer not null,
	id_type integer not null,

	val_when timestamp with time zone not null,
	val_num float,
	val_alpha text,
	val_unit text,
	val_normal_min float,
	val_normal_max float,
	val_normal_range text,
	technically_abnormal bool not null,
	note_provider text,

	reviewed_by_clinician bool,
	id_clinician integer,
	clinically_relevant bool
) inherits (audit_trail, log_dummy_clin_root_item);

-- ====================================
create table lab_result (
	id serial primary key,
	id_result integer not null references test_result(id),
	id_sampler integer default null,
	sample_id text not null default 'unknown',
	-- this is according to LDT
	abnormal_tag character(5)
) inherits (audit_mark, clin_root_item);

-- id_sampler -> identity.id

comment on table lab_result is
	'additional data for lab results';
comment on column lab_result.id_result is
	'which test result this lab data belongs to';
comment on column lab_result.sample_id IS
	'ID this sample had in the lab or when sent to the lab';
comment on column lab_result.id_sampler IS
	'who took the sample';
comment on column lab_result.abnormal_tag IS
	'tag attached by the lab whether value is considered pathological';

create table log_lab_result (
	id integer not null,
	id_result integer not null,
	id_sampler integer,
	sample_id text not null,
	abnormal_tag character(5)
) inherits (audit_trail, log_dummy_clin_root_item);

-- ====================================
-- ====================================
-- This is just an idea how measurements might be stored. It is far more
-- measurement-centric compared to gmLab, which might be not a good thing
-- for every-day use, but being more normalized and more strict it 
-- is probably better suitable for larger-scale clinical applications.

-- The main differences with gmLab are the following:
--
--     there is an additional table (here: test_action) which
--     normalizes the date/occasion at which several measurements were taken
--     In gmLab it might happen that the same sample is in the database as
--     being taken at different dates, since the date is stored for every
--     result

-- the doctor wants to see types of measurements grouped together
-- even if they come from different labs (maybe because she switched
-- labs at some point),
-- that's what this is for,

--create table test_unified (
--	id serial primary key,
--	short_name CHARACTER VARYING(10),
--	long_name CHARACTER VARYING(60),
--	comment CHARACTER VARYING(60)
--) INHERITS (audit_identity);

--COMMENT ON TABLE lab_test IS 'to unify tests accross lab result providers with different names for the same test';

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmMeasurements.sql,v $', '$Revision: 1.4 $');

-- =============================================
-- $Log: gmMeasurements.sql,v $
-- Revision 1.4  2003-07-27 21:59:47  ncq
-- - better comments/cleanup/renaming
-- - first remote FK defs
-- - auditing
--
-- Revision 1.3  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.2  2003/01/01 18:10:23  ncq
-- - changed to new i18n
-- - some field names more precise
--
-- Revision 1.1  2002/12/31 00:03:47  ncq
-- - merged gmLab and gmMeasure by Christof for more generic measurements storage
-- - gmLab deprecated
--
-- Revision 1.5  2002/12/22 01:24:25  ncq
-- - some changes suggested by Christof Meigen
--
-- Revision 1.4  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.3  2002/11/16 01:08:03  ncq
-- - fixup, revision tracking
--
