-- project: GNUMed
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)
-- identity related test data
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/gmDemographics-Person-test_data.sql,v $
-- $Id: gmDemographics-Person-test_data.sql,v 1.1 2003-10-31 22:53:27 ncq Exp $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ==========================================================
-- insert some example people
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Dr.', 'Ian', 'Haywood', '1977-12-19', 'UK', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Ms.', 'Cilla', 'Raby', '1979-3-1', 'AU', 'f');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Dr.', 'Horst', 'Herb', '1970-1-1', 'DE', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Dr.', 'Richard', 'Terry', '1960-1-1', 'AU', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Dr.', 'Karsten', 'Hilbert', '1974-10-23', 'DE', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Mr.', 'Sebastian', 'Hilbert', '1979-3-13', 'DE', 'm');
insert into v_basic_person (title, firstnames, lastnames, dob, cob, gender) values ('Dr.', 'Hilmar', 'Berger', '1974-1-1', 'DE', 'm');

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Person-test_data.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmDemographics-Person-test_data.sql,v $
-- Revision 1.1  2003-10-31 22:53:27  ncq
-- - started collection of test data
--
-- Revision 1.1  2003/08/02 10:46:03  ncq
-- - rename schema files by service
--
-- Revision 1.2  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.1  2003/02/14 10:36:37  ncq
-- - break out default and test data into their own files, needed for dump/restore of dbs
--
