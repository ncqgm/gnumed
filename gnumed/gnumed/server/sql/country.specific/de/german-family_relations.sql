-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-family_relations.sql,v $
-- $Revision: 1.2 $

-- part of GnuMed
-- GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- names of interpersonal relations translated into German
-- run this _after_ gmidentity.sql !
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into i18n_translations(lang, orig, trans) values('de_DE', 'parent', 'Elternteil');
insert into i18n_translations(lang, orig, trans) values('de_DE', 'sibling', 'Geschwister');
insert into i18n_translations(lang, orig, trans) values('de_DE', 'halfsibling', 'Stiefgeschwister');
insert into i18n_translations(lang, orig, trans) values('de_DE', 'stepparent', 'Stiefelter');
insert into i18n_translations(lang, orig, trans) values('de_DE', 'married', 'verheiratet');
insert into i18n_translations(lang, orig, trans) values('de_DE', 'de facto', 'de facto');
insert into i18n_translations(lang, orig, trans) values('de_DE', 'divorced', 'geschieden');
insert into i18n_translations(lang, orig, trans) values('de_DE', 'separated', 'getrennt');
insert into i18n_translations(lang, orig, trans) values('de_DE', 'legal guardian', 'Vormund');

-- =============================================
-- do simple revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: german-family_relations.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: german-family_relations.sql,v $
-- Revision 1.2  2003-05-12 12:43:40  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.1  2003/01/22 23:40:18  ncq
-- - first version
--
