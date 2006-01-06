-- project: GNUMed
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)
-- identity related test data
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/gmDemographics-Person-test_data.sql,v $
-- $Id: gmDemographics-Person-test_data.sql,v 1.8 2006-01-06 10:12:03 ncq Exp $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ==========================================================
-- insert some example people
insert into dem.v_basic_person (firstnames, lastnames, dob, cob, gender) values ('Ian', 'Haywood', '1977-12-19', 'UK', 'm');
insert into dem.v_basic_person (firstnames, lastnames, dob, cob, gender) values ('Cilla', 'Raby', '1979-3-1', 'AU', 'f');
insert into dem.v_basic_person (firstnames, lastnames, dob, cob, gender) values ('Horst', 'Herb', '1970-1-1', 'DE', 'm');
insert into dem.v_basic_person (firstnames, lastnames, dob, cob, gender) values ('Richard', 'Terry', '1960-1-1', 'AU', 'm');
insert into dem.v_basic_person (firstnames, lastnames, dob, cob, gender) values ('Karsten', 'Hilbert', '1974-10-23', 'DE', 'm');
insert into dem.v_basic_person (firstnames, lastnames, dob, cob, gender) values ('Sebastian', 'Hilbert', '1979-3-13', 'DE', 'm');
insert into dem.v_basic_person (firstnames, lastnames, dob, cob, gender) values ('Hilmar', 'Berger', '1974-1-1', 'DE', 'm');

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmDemographics-Person-test_data.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Person-test_data.sql,v $', '$Revision: 1.8 $');

-- =============================================
-- $Log: gmDemographics-Person-test_data.sql,v $
-- Revision 1.8  2006-01-06 10:12:03  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.7  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.6  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.5  2004/06/02 13:46:45  ncq
-- - setting default session timezone has incompatible syntax
--   across version range 7.1-7.4, henceforth specify timezone
--   directly in timestamp values, which works
--
-- Revision 1.4  2004/06/02 00:14:45  ncq
-- - add time zone setting
--
-- Revision 1.3  2004/01/08 22:58:28  ncq
-- - delete from gm_schema_revision
--
-- Revision 1.2  2003/11/23 23:35:11  ncq
-- - names.title -> identity.title
--
-- Revision 1.1  2003/10/31 22:53:27  ncq
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
