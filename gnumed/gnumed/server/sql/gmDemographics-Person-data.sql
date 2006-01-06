-- project: GNUMed
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)
-- identity related data
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Person-data.sql,v $
-- $Id: gmDemographics-Person-data.sql,v 1.10 2006-01-06 10:12:02 ncq Exp $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ================================================
-- please do NOT alter the sequence !!

BEGIN;
insert into dem.relation_types(biological, description, inverse) values(true,  i18n('parent'), NULL);
insert into dem.relation_types(biological, description, inverse) values(true,  i18n('child'), 1);
update dem.relation_types set inverse=2 where id=1;
insert into dem.relation_types(biological, description, inverse) values(true,  i18n('sibling'), 3);
insert into dem.relation_types(biological, description, inverse) values(true,  i18n('halfsibling'), 4);
insert into dem.relation_types(biological, description, inverse) values(false, i18n('stepparent'), NULL);
insert into dem.relation_types(biological, description, inverse) values(false, i18n('stepchild'), 5);
update dem.relation_types set inverse=6 where id=5;
insert into dem.relation_types(biological, description, inverse) values(false, i18n('married'), 7);
insert into dem.relation_types(biological, description, inverse) values(false, i18n('de facto'), 8);
insert into dem.relation_types(biological, description, inverse) values(false, i18n('divorced'), 9);
insert into dem.relation_types(biological, description, inverse) values(false, i18n('separated'), 10);
insert into dem.relation_types(biological, description, inverse) values(false, i18n('legal guardian'), NULL);
insert into dem.relation_types(biological, description, inverse) values(false, i18n('ward'), 11);
update dem.relation_types set inverse=12 where id=11;
COMMIT;

insert into dem.marital_status(name) values (i18n ('single'));
insert into dem.marital_status(name) values (i18n ('de facto'));
insert into dem.marital_status(name) values (i18n ('married'));
insert into dem.marital_status(name) values (i18n ('divorced'));
insert into dem.marital_status(name) values (i18n ('separated'));
insert into dem.marital_status(name) values (i18n ('widowed'));


insert into dem.gender_label (tag, label, sort_weight, comment) values (
	i18n('m'), i18n('male'), 3, '(m)ale'
);
insert into dem.gender_label (tag, label, sort_weight, comment) values (
	i18n('f'), i18n('female'), 3, '(f)emale'
);
insert into dem.gender_label (tag, label, sort_weight, comment) values (
	i18n('tm'), i18n('transsexual phenotype male'), 2, 'tm - (t)ranssexual phenotype (m)ale'
);
insert into dem.gender_label (tag, label, sort_weight, comment) values (
	i18n('tf'), i18n('transsexual phenotype female'), 2, 'tf - (t)ranssexual phenotype (f)emale'
);
insert into dem.gender_label (tag, label, sort_weight, comment) values (
	i18n('h'), i18n('hermaphrodite'), 1, '(h)ermaphrodite: intersexual'
);

-- ===================================================================
-- staff roles
delete from dem.staff_role;

-- standard GP practice staff
insert into dem.staff_role (name) values (i18n('doctor'));
insert into dem.staff_role (name) values (i18n('nurse'));
insert into dem.staff_role (name) values (i18n('manager'));
insert into dem.staff_role (name) values (i18n('secretary'));
insert into dem.staff_role (name) values (i18n('X-ray assistant'));
insert into dem.staff_role (name) values (i18n('lab technician'));
insert into dem.staff_role (name) values (i18n('medical student'));
insert into dem.staff_role (name) values (i18n('student nurse'));
insert into dem.staff_role (name) values (i18n('trainee - secretary'));
insert into dem.staff_role (name) values (i18n('trainee - X-ray'));
insert into dem.staff_role (name) values (i18n('trainee - lab'));

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Person-data.sql,v $', '$Revision: 1.10 $');

-- =============================================
-- $Log: gmDemographics-Person-data.sql,v $
-- Revision 1.10  2006-01-06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.9  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.8  2005/07/14 21:31:42  ncq
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
