-- project: GNUMed
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)
-- identity related data
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Person-data.sql,v $
-- $Id: gmDemographics-Person-data.sql,v 1.1 2003-08-02 10:46:03 ncq Exp $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ================================================
-- please do NOT alter the sequence !!

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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Person-data.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmDemographics-Person-data.sql,v $
-- Revision 1.1  2003-08-02 10:46:03  ncq
-- - rename schema files by service
--
-- Revision 1.3  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.2  2003/05/03 14:24:56  ncq
-- - updated comment
--
-- Revision 1.1  2003/02/14 10:36:37  ncq
-- - break out default and test data into their own files, needed for dump/restore of dbs
--
