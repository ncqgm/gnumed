-- project: GNUMed
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)
-- identity related data
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmIdentityData.sql,v $
-- $Id: gmIdentityData.sql,v 1.1 2003-02-14 10:36:37 ncq Exp $
-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ================================================
-- TRANSLATORS: please do NOT alter the sequence or insert anything; just translate!
-- Only that way we will be able to exchange relationship details between multilingual
-- databases. Hopefully, we will soon have an ontology taking care of this problem.

insert into relation_types(biological, description) values(true,  i18n('parent'));
insert into relation_types(biological, description) values(true,  i18n('sibling'));
insert into relation_types(biological, description) values(true,  i18n('halfsibling'));
insert into relation_types(biological, description) values(false, i18n('stepparent'));
insert into relation_types(biological, description) values(false, i18n('married'));
insert into relation_types(biological, description) values(false, i18n('de facto'));
insert into relation_types(biological, description) values(false, i18n('divorced'));
insert into relation_types(biological, description) values(false, i18n('separated'));
insert into relation_types(biological, description) values(false, i18n('legal guardian'));

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmIdentityData.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmIdentityData.sql,v $
-- Revision 1.1  2003-02-14 10:36:37  ncq
-- - break out default and test data into their own files, needed for dump/restore of dbs
--
