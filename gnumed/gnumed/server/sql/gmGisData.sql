-- project: GNUMed
-- database: GIS
-- purpose:  geographic information (mostly of type 'address')

-- license: GPL (details at http://gnu.org)
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmGisData.sql,v $
-- $Id $
-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
 -- do not alter the id of home !
INSERT INTO address_type(id, name) values(1, i18n('home'));
INSERT INTO address_type(id, name) values(2, i18n('work'));
INSERT INTO address_type(id, name) values(3, i18n('parents'));
INSERT INTO address_type(id, name) values(4, i18n('holidays'));
INSERT INTO address_type(id, name) values(5, i18n('temporary'));

-- ===================================================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmGisData.sql,v $', '$Revision: 1.1 $');

-- ===================================================================
-- $Log: gmGisData.sql,v $
-- Revision 1.1  2003-02-14 10:46:17  ncq
-- - breaking out enumeration data
--
