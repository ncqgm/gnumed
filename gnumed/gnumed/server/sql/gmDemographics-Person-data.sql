-- project: GNUMed
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)
-- identity related data
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Person-data.sql,v $
-- $Id: gmDemographics-Person-data.sql,v 1.8 2005-07-14 21:31:42 ncq Exp $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ================================================
-- please do NOT alter the sequence !!

BEGIN;
insert into relation_types(biological, description, inverse) values(true,  i18n('parent'), NULL);
insert into relation_types(biological, description, inverse) values(true,  i18n('child'), 1);
update relation_types set inverse=2 where id=1;
insert into relation_types(biological, description, inverse) values(true,  i18n('sibling'), 3);
insert into relation_types(biological, description, inverse) values(true,  i18n('halfsibling'), 4);
insert into relation_types(biological, description, inverse) values(false, i18n('stepparent'), NULL);
insert into relation_types(biological, description, inverse) values(false, i18n('stepchild'), 5);
update relation_types set inverse=6 where id=5;
insert into relation_types(biological, description, inverse) values(false, i18n('married'), 7);
insert into relation_types(biological, description, inverse) values(false, i18n('de facto'), 8);
insert into relation_types(biological, description, inverse) values(false, i18n('divorced'), 9);
insert into relation_types(biological, description, inverse) values(false, i18n('separated'), 10);
insert into relation_types(biological, description, inverse) values(false, i18n('legal guardian'), NULL);
insert into relation_types(biological, description, inverse) values(false, i18n('ward'), 11);
update relation_types set inverse=12 where id=11;
COMMIT;

insert into marital_status(name) values (i18n ('single'));
insert into marital_status(name) values (i18n ('de facto'));
insert into marital_status(name) values (i18n ('married'));
insert into marital_status(name) values (i18n ('divorced'));
insert into marital_status(name) values (i18n ('separated'));
insert into marital_status(name) values (i18n ('widowed'));


insert into gender_label (tag, label, sort_weight, comment) values (
	i18n('m'), i18n('male'), 3, '(m)ale'
);
insert into gender_label (tag, label, sort_weight, comment) values (
	i18n('f'), i18n('female'), 3, '(f)emale'
);
insert into gender_label (tag, label, sort_weight, comment) values (
	i18n('tm'), i18n('transsexual phenotype male'), 2, 'tm - (t)ranssexual phenotype (m)ale'
);
insert into gender_label (tag, label, sort_weight, comment) values (
	i18n('tf'), i18n('transsexual phenotype female'), 2, 'tf - (t)ranssexual phenotype (f)emale'
);
insert into gender_label (tag, label, sort_weight, comment) values (
	i18n('h'), i18n('hermaphrodite'), 1, '(h)ermaphrodite: intersexual'
);

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmDemographics-Person-data.sql,v $', '$Revision: 1.8 $', True);

-- =============================================
-- $Log: gmDemographics-Person-data.sql,v $
-- Revision 1.8  2005-07-14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.7  2005/04/14 17:45:21  ncq
-- - gender_label.sort_rank -> sort_weight
--
-- Revision 1.6  2005/04/14 16:57:50  ncq
-- - add gender_label data
--
-- Revision 1.5  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.4  2004/12/20 19:04:37  ncq
-- - fixes by Ian while overhauling the demographics API
--
-- Revision 1.3  2004/12/15 09:25:53  ncq
-- - don't hardcode primary key of marital status
--
-- Revision 1.2  2004/03/02 10:22:30  ihaywood
-- support for martial status and occupations
-- .conf files now use host autoprobing
--
-- Revision 1.1  2003/08/02 10:46:03  ncq
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
