-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-encounter_types.sql,v $
-- $Revision: 1.1 $

-- part of GnuMed
-- GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- clinical encounter types translated into German
-- run this _after_ gmclinical.sql !
-- =============================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'surgery consultation', 'Praxisbesuch');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'phone consultation', 'Anruf');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'fax consultation', 'per Fax');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'home visit', 'Hausbesuch');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'nursing home visit', 'Heimbesuch');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'repeat script', 'Wiederholungsrezept');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'hospital visit', 'Krankenhausbesuch');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'video conference', 'per Video');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'proxy encounter', 'indirekt');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'emergency encounter', 'Notfall');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'other encounter', 'anderer Kontakt'); -- such as at the mall :-))

-- =============================================
-- do simple revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: german-encounter_types.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: german-encounter_types.sql,v $
-- Revision 1.1  2003-01-26 15:02:58  ncq
-- - first translation
--
