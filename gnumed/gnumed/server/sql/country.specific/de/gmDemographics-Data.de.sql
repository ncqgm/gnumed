-- GnuMed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmDemographics-Data.de.sql,v $
-- $Revision: 1.1 $

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- =============================================
-- names of interpersonal relations translated into German
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Data.de.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmDemographics-Data.de.sql,v $
-- Revision 1.1  2003-08-05 08:16:00  ncq
-- - cleanup/renaming
--
-- Revision 1.3  2003/06/11 14:03:44  ncq
-- - set encoding
--
-- Revision 1.2  2003/05/12 12:43:40  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.1  2003/01/22 23:40:18  ncq
-- - first version
--
