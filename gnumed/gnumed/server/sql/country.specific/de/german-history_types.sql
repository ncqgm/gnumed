-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-history_types.sql,v $
-- $Revision: 1.2 $

-- part of GnuMed
-- GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- patient history types translated into German
-- run this _after_ gmclinical.sql !
-- =============================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'presenting complaint', 'jetzige Beschwerden');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'history of present illness', 'Jetzt-Anamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'past', '? Eigenanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'social', 'Sozialanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'family', 'Familienanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'immunisation', 'Impfanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'requests', '?? requests');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'allergy', 'Allergieanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'drug', '?? Drogenanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'sexual', 'Sexualanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'psychiatric', 'psychiatrische Anamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'other', 'sonstige Anamnese');

-- =============================================
-- do simple revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: german-history_types.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: german-history_types.sql,v $
-- Revision 1.2  2003-01-26 15:35:49  ncq
-- - typo
--
-- Revision 1.1  2003/01/26 15:33:52  ncq
-- - some more translations for gmclinical.sql
--
