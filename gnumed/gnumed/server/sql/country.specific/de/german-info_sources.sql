-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-info_sources.sql,v $
-- $Revision: 1.1 $

-- part of GnuMed
-- GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- patient history info sources translated into German
-- run this _after_ gmclinical.sql !
-- =============================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'patient', 'Patient');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'clinician', 'Mediziner');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'relative', 'Angehörige');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'carer', 'Pflegeperson');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'notes', 'Unterlagen');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'correspondence', 'Korrespondenz');

-- =============================================
-- do simple revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: german-info_sources.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: german-info_sources.sql,v $
-- Revision 1.1  2003-01-26 15:33:52  ncq
-- - some more translations for gmclinical.sql
--
