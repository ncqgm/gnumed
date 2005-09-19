-- =============================================
-- GNUmed: Diagnosen

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmDiagnosen.sql,v $
-- $Revision: 1.3 $

-- license: GPL
-- author (of script file): Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- =============================================
select add_coded_term('Harnwegsinfekt', 'N39.0', 'ICD10-GM 2004');
select add_coded_term('Pollinosis', 'J30.1', 'ICD-10-GM 2004');
select add_coded_term('Basedow-Struma', 'E05.0', 'ICD-10-GM 2004');
select add_coded_term('Strumaresektion', 'Z98.8', 'ICD-10-GM 2004');
select add_coded_term('Follikuläres Schilddrüsenkarzinom', 'C73', 'ICD-10-GM 2004');
select add_coded_term('Hyperlipidämie', 'E78.5', 'ICD-10-GM 2004');
select add_coded_term('Diabetes mellitus nnb', 'E14.9', 'ICD-10-GM 2004');
select add_coded_term('Reizblase', 'R30.0', 'ICD-10-GM 2004');
select add_coded_term('Hyperthyreose', 'E05.9', 'ICD-10-GM 2004');
select add_coded_term('Hypercholesterinämie', 'E78.0', 'ICD-10-GM 2004');
select add_coded_term('Hypocalzämie', 'R79.0', 'ICD-10-GM 2004');
select add_coded_term('Strumaresektion', 'E89.-', 'ICD-10-GM 2004');
select add_coded_term('Lymphangitis', 'I89.1', 'ICD-10-GM 2004');
select add_coded_term('Check up', 'Z00.-', 'ICD-10-GM 2004');
select add_coded_term('Nikotinabusus', 'F17.2', 'ICD-10-GM 2004');
select add_coded_term('psychovegetatives Syndrom', 'F45.1', 'ICD-10-GM 2004');
select add_coded_term('Depressive Verstimmung', 'F32.9', 'ICD-10-GM 2004');
select add_coded_term('Leistungsknick', 'R53', 'ICD-10-GM 2004');

--select add_coded_term('', '', 'ICD-10-GM 2004');
--select add_coded_term('', '', 'ICD-10-GM 2004');
--select add_coded_term('', '', 'ICD-10-GM 2004');
--select add_coded_term('', '', 'ICD-10-GM 2004');
--select add_coded_term('', '', 'ICD-10-GM 2004');
--select add_coded_term('', '', 'ICD-10-GM 2004');

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmDiagnosen.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES ('$RCSfile: gmDiagnosen.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: gmDiagnosen.sql,v $
-- Revision 1.3  2005-09-19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.2  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.1  2005/04/06 10:41:19  ncq
-- - add a bunch of diagnoses coded ICD-10-GM
--
