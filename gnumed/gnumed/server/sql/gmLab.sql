-- lab related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmLab.sql,v $
-- $Revision: 1.4 $
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

CREATE TABLE lab (
	id serial primary key,
	practice_id INTEGER REFERENCES practice_dummy,
	adm_contact INTEGER REFERENCES identity,
	med_contact INTEGER REFERENCES identity
) INHERITS (audit_identity);

COMMENT ON TABLE lab IS 'one specific lab with contact information';
COMMENT ON COLUMN lab.practice_id IS 'address of lab';
COMMENT ON COLUMN lab.adm_contact IS 'whom to call for admin questions (modem link, etc.)';
COMMENT ON COLUMN lab.med_contact IS 'whom to call for medical questions (result verification, additional test requests)';

-- ====================================
CREATE TABLE lab_test (
	id serial primary key,
	short_name CHARACTER VARYING(10),
	long_name CHARACTER VARYING(60),
	comment CHARACTER VARYING(60)
) INHERITS (audit_identity);

COMMENT ON TABLE lab_test IS 'to unify tests accross lab result providers with different names for the same test';
COMMENT ON COLUMN lab_test.short_name IS 'short name to be displayed in clients, eg HB';
COMMENT ON COLUMN lab_test.long_name IS 'long name unmistakingly identifying this test, eg Venous Hemoglobin, useful for literature research etc.';

-- =============================================
CREATE TABLE lab_unit (
	id serial primary key,
	name CHARACTER VARYING(20)
) INHERITS (audit_identity);

-- ====================================
CREATE TABLE lab_specific_test (
	lab_id INTEGER NOT NULL REFERENCES lab,
	test_id INTEGER NOT NULL REFERENCES lab_test,
	unit_id INTEGER REFERENCES lab_unit,
	short_name CHARACTER VARYING(10),
	long_name CHARACTER VARYING(60),
	range_female CHARACTER VARYING(10),
	range_male CHARACTER VARYING(10),
	comment CHARACTER VARYING(60)
) INHERITS (audit_identity);

COMMENT ON TABLE lab_specific_test IS 'description of a test as provided by a specific lab, this table can be built either from an ELV (Elektronisches LeistungsVerzeichnis = electronic methods directory) provided by the labs or dynamically during import of lab results, or manually of course';
COMMENT ON COLUMN lab_specific_test.lab_id IS 'link to lab record';
COMMENT ON COLUMN lab_specific_test.test_id IS 'link to test in our practice';
COMMENT ON COLUMN lab_specific_test.short_name IS 'short name as provided by a specific lab';
COMMENT ON COLUMN lab_specific_test.long_name IS 'long name as provided by a specific lab';

-- ====================================
CREATE TABLE lab_result (
	pat_id INTEGER REFERENCES identity,
	episode_id INTEGER REFERENCES episode_dummy default 0,
	test_id INTEGER REFERENCES lab_test,
	lab_id INTEGER REFERENCES lab,
	sample_id CHARACTER VARYING(25) NOT NULL default 'not available',
	sample_date DATE NOT NULL,
	result_date DATE NOT NULL,
	value CHARACTER(15) NOT NULL,
	unit CHARACTER(10) NOT NULL REFERENCES lab_unit,
	abnormal_tag CHARACTER(5),
	lab_comment TEXT,
	comment TEXT
) INHERITS (audit_identity);
-- episode 0 == 'unattached'

COMMENT ON TABLE lab_result is 'one specific instance of lab_test';

COMMENT ON COLUMN lab_result.pat_id IS 'the patient this test belongs to';
COMMENT ON COLUMN lab_result.episode_id IS 'the episode of care this lab result belongs to';
COMMENT ON COLUMN lab_result.test_id IS 'link to test in our practice';
COMMENT ON COLUMN lab_result.lab_id IS 'the lab which provided this result';

COMMENT ON COLUMN lab_result.sample_id IS 'ID this sample had in the lab or when sent to the lab';
COMMENT ON COLUMN lab_result.sample_date IS 'date/time sample was taken';
COMMENT ON COLUMN lab_result.result_date IS 'date/time result was produced';

COMMENT ON COLUMN lab_result.unit IS 'if we normalize this into it s own field we may later on be able to leverage it for clinical calculations';
COMMENT ON COLUMN lab_result.abnormal_tag IS 'tag attached by the lab whether value is considered pathological';
COMMENT ON COLUMN lab_result.lab_comment IS 'verbal evaluation of result by lab staff (doc, technician or comment such as "contaminated sample"';
COMMENT ON COLUMN lab_result.comment IS 'what WE think about this result';

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmLab.sql,v $', '$Revision: 1.4 $');

-- =============================================
-- $Log: gmLab.sql,v $
-- Revision 1.4  2002-12-01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.3  2002/11/16 01:08:03  ncq
-- - fixup, revision tracking
--
