-- GnuMed lab related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- author: Christof Meigen <christof@nicht-ich.de>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmMeasurements.sql,v $
-- $Revision: 1.3 $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
CREATE TABLE practice_dummy (
	id serial primary key,
	dummy varchar(10)
);

CREATE TABLE episode_dummy (
	id serial primary key,
	dummy varchar(10)
);

create table dummy_clinical_transaction (
	id serial primary key
);

-- ====================================
CREATE TABLE measurement_org (
	id serial primary key,
	practice_id INTEGER REFERENCES practice_dummy,
	adm_contact INTEGER REFERENCES identity,
	med_contact INTEGER REFERENCES identity,
	"comment" varchar(60)
);

COMMENT ON TABLE measurement_org IS 'organisation providing results';
COMMENT ON COLUMN measurement_org.practice_id IS 'address or organisation';
COMMENT ON COLUMN measurement_org.adm_contact IS 'whom to call for admin questions (modem link, etc.)';
COMMENT ON COLUMN measurement_org.med_contact IS 'whom to call for medical questions (result verification, additional test requests)';
comment on column measurement_org."comment" is
	'useful for, say, dummy records, where you want to mark up stuff like "pharmacy such-and-such" if you don''t have it in your contacts';

-- there need to be two pseudo org records
--  1) your own practice
--  2) "non-medical person" (_who_ is in *_result)

-- ====================================
CREATE TABLE measurement_basic_unit (
	id serial primary key,
	name_short varchar(10) not null,
	name_long varchar(30)
);
COMMENT ON TABLE measurement_basic_unit IS
	'basic units are SI units, units derived from them and the Unity.';

-- ====================================
create table measurement_unit (
	id serial primary key,
	id_basic_unit integer references measurement_basic_unit,
	name_short varchar(10) not null,
	name_long varchar(30),
	factor float NOT NULL,
	shift float NOT NULL
);
COMMENT ON TABLE measurement_unit IS 
	'units as used in results of tests/measurements';
COMMENT ON column measurement_unit.id_basic_unit IS 
	'what is the SI-Standard unit for this, e.g. for the unit mg it is kg';
COMMENT ON column measurement_unit.factor IS 
	'what factor the value with this unit has to be multiplied with to get values in the basic_unit';
COMMENT ON column measurement_unit.shift IS 
	'what has to be added (after multiplying by factor) to a value with this unit to get values in the basic_unit';

-- ====================================
create table measurement_type (
	id serial primary key,
	id_org integer references measurement_org,
	name_short varchar(10) not null,
	name_long varchar(60),
	"comment" varchar(60),
	basic_unit integer references measurement_basic_unit,
	aux_data_type varchar(10)
);
comment on table measurement_type is
	'metadata about a measurement type';
comment on column measurement_type.aux_data_type is
	'suffix of table holding additional data about this type of measurement, eg "lab" -> "measurement_result_lab" has more data';

-- ====================================
create table measurement_result (
	id serial primary key,
	id_clinical_transaction integer references dummy_clinical_transaction,
	id_type integer references measurement_type,
	id_patient integer references identity,
	id_provider integer references identity,

	val_numeric float,
	val_alpha varchar(20),
	val_normal_max float,
	val_normal_min float,
	comment_provider text,
	comment_clinician text,
	technically_abnormal bool,
	clinically_relevant bool,
);
-- date/time measurement was taken is in clinical_transaction->date
COMMENT ON TABLE  measurement_result is 
	'the results of a single measurement';

-- ====================================
create table measurement_result_lab (
	id_sample varchar(25) NOT NULL default 'not available',
	id_sampler integer references identity,
	abnormal_tag character(5)		-- this is according to LDT
);

comment on table measurement_result_lab is
	'additional data for lab results';
comment on column measurement_result_lab.id_sample IS
	'ID this sample had in the lab or when sent to the lab';
comment on column measurement_result_lab.id_sampler IS
	'who took the sample';
comment on column measurement_result_lab.abnormal_tag IS
	'tag attached by the lab whether value is considered pathological';

-- ====================================
-- ====================================
-- This is just an idea how measurements might be stored. It is far more
-- measurement-centric compared to gmLab, which might be not a good thing
-- for every-day use, but being more normalized and more strict it 
-- is probably better suitable for larger-scale clinical applications.

-- The main differences with gmLab are the following:
--
--     there is an additional table (here: measurement_action) which
--     normalizes the date/occasion at which several measurements were taken
--     In gmLab it might happen that the same sample is in the database as
--     being taken at different dates, since the date is stored for every
--     result
--
--     there is a further normalisation concerning units, which enables
--     automatic conversion between different units and restriction
--     of units for a parameter (e.g. body mass can be in g and kg, 
--     but not in mol/l, since it is a mass)
--
--     values of measurement results are stored as floats in order
--     to avoid data like "1,764.5" vs "1'764,5" etc. (not to speak of
--     "l,764,S")
--
--     the minimum/maximum normal value according to the Lab are stored for each 
--     measurement. This might be good since at least some labs have
--     age-dependent norms and do not publish them (In any way I hope that 
--     most people will use norms provided by GnuMed) So, while this indeed
--     may lead to inconsistencies, these inconsistencies might be due to 
--     the Lab changing norms at it's will without notice, or not telling 
--     how to calculate the norms etc.
--
--     measurement results can be attached to several medical episodes     
--     
--     lab data is not mandatory for every measurement. This might reduce
--     space quite a lot, since 1'000'000 measurment results is not absurd
--     in clinical applications and just adding 'not available' as sampleId
--     for every result would increase database-size by 14MB.


-- I hope that some of the ideas can be merged into gmLab.



-- the doctor wants to see types of measurements grouped together
-- even if they come from different labs (maybe because she switched
-- labs at some point),
-- that's what this is for,

--CREATE TABLE measurement_unified (
--	id serial primary key,
--	short_name CHARACTER VARYING(10),
--	long_name CHARACTER VARYING(60),
--	comment CHARACTER VARYING(60)
--) INHERITS (audit_identity);

--COMMENT ON TABLE lab_test IS 'to unify tests accross lab result providers with different names for the same test';
--COMMENT ON COLUMN lab_test.short_name IS 'short name to be displayed in clients, eg HB';
--COMMENT ON COLUMN lab_test.long_name IS 'long name unmistakingly identifying this test, eg Venous Hemoglobin, useful for literature research etc.';

--COMMENT ON TABLE lab_specific_test IS
--	'description of a test as provided by a specific lab,
--	 this table can be built either from an ELV (Elektronisches LeistungsVerzeichnis = electronic methods directory)
--	 provided by the labs or dynamically during import of lab results, or manually of course';
--COMMENT ON COLUMN lab_specific_test.lab_id IS
--	'link to lab record';
--COMMENT ON COLUMN lab_specific_test.test_id IS
----	'link to test in our practice';
--COMMENT ON COLUMN lab_specific_test.short_name IS
--	'short name as provided by a specific lab';
--COMMENT ON COLUMN lab_specific_test.long_name IS
--	'long name as provided by a specific lab';

-- ====================================
--COMMENT ON TABLE lab_result is 'one specific instance of lab_test';
--COMMENT ON COLUMN lab_result.pat_id IS 'the patient this test belongs to';
--COMMENT ON COLUMN lab_result.id_clinical_transaction IS 'the clinical transaction this lab result belongs to';
--COMMENT ON COLUMN lab_result.lab_id IS 'the lab which provided this result';
--COMMENT ON COLUMN lab_result.result_date IS 'date/time result was produced';
--COMMENT ON COLUMN lab_result.unit IS
--	'if we normalize this into it"s own field we may later on be able to leverage it for clinical calculations';
--COMMENT ON COLUMN lab_result.lab_comment IS
--	'verbal evaluation of result by lab staff (doc, technician or comment such as "contaminated sample"';

--COMMENT ON COLUMN lab_result.doc_abnormal_flag IS
--	'whether the treating doctor considers this value clinically relevantly abnormal for this patient at this point in time';
--COMMENT ON COLUMN lab_result.doc_comment IS
--	'what the doc thinks about this result';

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmMeasurements.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: gmMeasurements.sql,v $
-- Revision 1.3  2003-01-05 13:05:51  ncq
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
