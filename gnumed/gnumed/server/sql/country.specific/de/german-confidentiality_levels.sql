-- ==================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-confidentiality_levels.sql,v $
-- $Revision: 1.1 $

-- part of GnuMed
-- GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- confidentiality levels translated into German
-- run this gmclinical.sql ?????.sql !
-- =============================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'public', 'öffentlich');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'relatives', 'Angehörige');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'receptionist', 'Personal');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'clinical staff', 'klinisches Personal');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'doctors', 'Ärzte');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'doctors of practice only', 'Ärzte dieser Einrichtung');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'treating doctor', 'behandelnder Arzt');

-- =============================================
-- do simple revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: german-confidentiality_levels.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: german-confidentiality_levels.sql,v $
-- Revision 1.1  2003-01-26 15:33:52  ncq
-- - some more translations for gmclinical.sql
--
