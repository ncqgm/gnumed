-- =============================================
-- GNUmed: Diagnosen

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmDiagnosen.sql,v $
-- $Revision: 1.5 $

-- license: GPL
-- author (of script file): Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- =============================================
select clin.add_coded_term('Harnwegsinfekt', 'N39.0', 'ICD10-GM 2004');
select clin.add_coded_term('Pollinosis', 'J30.1', 'ICD-10-GM 2004');
select clin.add_coded_term('Basedow-Struma', 'E05.0', 'ICD-10-GM 2004');
select clin.add_coded_term('Strumaresektion', 'Z98.8', 'ICD-10-GM 2004');
select clin.add_coded_term('Follikuläres Schilddrüsenkarzinom', 'C73', 'ICD-10-GM 2004');
select clin.add_coded_term('Hyperlipidämie', 'E78.5', 'ICD-10-GM 2004');
select clin.add_coded_term('Diabetes mellitus nnb', 'E14.9', 'ICD-10-GM 2004');
select clin.add_coded_term('Reizblase', 'R30.0', 'ICD-10-GM 2004');
select clin.add_coded_term('Hyperthyreose', 'E05.9', 'ICD-10-GM 2004');
select clin.add_coded_term('Hypercholesterinämie', 'E78.0', 'ICD-10-GM 2004');
select clin.add_coded_term('Hypocalzämie', 'R79.0', 'ICD-10-GM 2004');
select clin.add_coded_term('Strumaresektion', 'E89.-', 'ICD-10-GM 2004');
select clin.add_coded_term('Lymphangitis', 'I89.1', 'ICD-10-GM 2004');
select clin.add_coded_term('Check up', 'Z00.-', 'ICD-10-GM 2004');
select clin.add_coded_term('Nikotinabusus', 'F17.2', 'ICD-10-GM 2004');
select clin.add_coded_term('psychovegetatives Syndrom', 'F45.1', 'ICD-10-GM 2004');
select clin.add_coded_term('Depressive Verstimmung', 'F32.9', 'ICD-10-GM 2004');
select clin.add_coded_term('Leistungsknick', 'R53', 'ICD-10-GM 2004');
select clin.add_coded_term('Masern', 'B05', 'ICD-10-GM 2004');
select clin.add_coded_term('Masern', 'B05+', 'ICD-10-GM 2004');
select clin.add_coded_term('Masern', 'B05.1+', 'ICD-10-GM 2004');
select clin.add_coded_term('Masern', 'B05.2+', 'ICD-10-GM 2004');
select clin.add_coded_term('Masern', 'B05.3+', 'ICD-10-GM 2004');
select clin.add_coded_term('Masern', 'B05.4+', 'ICD-10-GM 2004');
select clin.add_coded_term('Masern', 'B05.8+', 'ICD-10-GM 2004');
select clin.add_coded_term('Masern', 'B05.9+', 'ICD-10-GM 2004');
select clin.add_coded_term('Mumps', 'B26', 'ICD-10-GM 2004');
select clin.add_coded_term('Mumps', 'B26.0+', 'ICD-10-GM 2004');
select clin.add_coded_term('Mumps', 'B26.1+', 'ICD-10-GM 2004');
select clin.add_coded_term('Mumps', 'B26.2+', 'ICD-10-GM 2004');
select clin.add_coded_term('Mumps', 'B26.3+', 'ICD-10-GM 2004');
select clin.add_coded_term('Mumps', 'B26.8', 'ICD-10-GM 2004');
select clin.add_coded_term('Mumps', 'B26.9', 'ICD-10-GM 2004');
select clin.add_coded_term('Röteln', 'B06', 'ICD-10-GM 2004');
select clin.add_coded_term('Röteln', 'B06.0+', 'ICD-10-GM 2004');
select clin.add_coded_term('Röteln', 'B06.8', 'ICD-10-GM 2004');
select clin.add_coded_term('Röteln', 'B06.9', 'ICD-10-GM 2004');
select clin.add_coded_term('Tetanus', 'A33', 'ICD-10-GM 2004');
select clin.add_coded_term('Tetanus', 'A34', 'ICD-10-GM 2004');
select clin.add_coded_term('Tetanus', 'A35', 'ICD-10-GM 2004');
select clin.add_coded_term('Diphtherie', 'A36', 'ICD-10-GM 2004');
select clin.add_coded_term('Diphtherie', 'A36.0', 'ICD-10-GM 2004');
select clin.add_coded_term('Diphtherie', 'A36.1', 'ICD-10-GM 2004');
select clin.add_coded_term('Diphtherie', 'A36.2', 'ICD-10-GM 2004');
select clin.add_coded_term('Diphtherie', 'A36.3', 'ICD-10-GM 2004');
select clin.add_coded_term('Diphtherie', 'A36.8', 'ICD-10-GM 2004');
select clin.add_coded_term('Diphtherie', 'A36.9', 'ICD-10-GM 2004');
select clin.add_coded_term('Influenza', 'J11', 'ICD-10-GM 2004');
select clin.add_coded_term('Influenza', 'J11.0', 'ICD-10-GM 2004');
select clin.add_coded_term('Influenza', 'J11.1', 'ICD-10-GM 2004');
select clin.add_coded_term('Influenza', 'J11.8', 'ICD-10-GM 2004');
select clin.add_coded_term('Pertussis', 'A37', 'ICD-10-GM 2004');
select clin.add_coded_term('Pertussis', 'A37.0', 'ICD-10-GM 2004');
select clin.add_coded_term('Pertussis', 'A37.1', 'ICD-10-GM 2004');
select clin.add_coded_term('Pertussis', 'A37.8', 'ICD-10-GM 2004');
select clin.add_coded_term('Pertussis', 'A37.9', 'ICD-10-GM 2004');
select clin.add_coded_term('Hepatitis A', 'B15', 'ICD-10-GM 2004');
select clin.add_coded_term('Hepatitis A', 'B15.0', 'ICD-10-GM 2004');
select clin.add_coded_term('Hepatitis A', 'B15.9', 'ICD-10-GM 2004');
select clin.add_coded_term('Meningokokkeninfektion', 'A39', 'ICD-10-GM 2004');
select clin.add_coded_term('Meningokokkenmeningitis', 'A39.0+', 'ICD-10-GM 2004');
select clin.add_coded_term('Waterhouse-Friderichsen-Syndrom', 'A39.1+', 'ICD-10-GM 2004');
select clin.add_coded_term('akute Meningokokkensepsis', 'A39.2', 'ICD-10-GM 2004');
select clin.add_coded_term('chronische Meningokokkensepsis', 'A39.3', 'ICD-10-GM 2004');
select clin.add_coded_term('Meningokokkensepsis', 'A39.4', 'ICD-10-GM 2004');
select clin.add_coded_term('Herzkrankheit durch Meningokokken', 'A39.5+', 'ICD-10-GM 2004');
select clin.add_coded_term('sonstige Meningokokkeninfektionen', 'A39.8', 'ICD-10-GM 2004');
select clin.add_coded_term('Meningokokkeninfektion', 'A39.9', 'ICD-10-GM 2004');

--select clin.add_coded_term('', '', 'ICD-10-GM 2004');
--select clin.add_coded_term('', '', 'ICD-10-GM 2004');
--select clin.add_coded_term('', '', 'ICD-10-GM 2004');
--select clin.add_coded_term('', '', 'ICD-10-GM 2004');
--select clin.add_coded_term('', '', 'ICD-10-GM 2004');
--select clin.add_coded_term('', '', 'ICD-10-GM 2004');

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmDiagnosen.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES ('$RCSfile: gmDiagnosen.sql,v $', '$Revision: 1.5 $');

-- =============================================
-- $Log: gmDiagnosen.sql,v $
-- Revision 1.5  2006-02-10 14:10:26  ncq
-- - add what was linked to vacc_indication previously
--
-- Revision 1.4  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.3  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.2  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.1  2005/04/06 10:41:19  ncq
-- - add a bunch of diagnoses coded ICD-10-GM
--
