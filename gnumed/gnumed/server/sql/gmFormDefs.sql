-- ===================================================
-- GnuMed form templates related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- author: Ian Haywood <>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmFormDefs.sql,v $
-- $Revision: 1.11 $
-- ===================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================
create table lnk_form2discipline (
	pk serial primary key,
	fk_form integer references form_defs(pk),
	discipline text
);

comment on table lnk_form2discipline is
	'the discipline which uses this form. This maps to
	 gmDemographics.occupation for individuals,
	 gmDemographics.category for organisations';

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmFormDefs.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmFormDefs.sql,v $', '$Revision: 1.11 $');

-- =============================================
-- * do we need "form_defs.iso_countrycode" ?
-- * good/bad decision to use point/box PG data type ?

-- =============================================
-- $Log: gmFormDefs.sql,v $
-- Revision 1.11  2006-01-13 11:17:18  ncq
-- - remove misleading comment
--
-- Revision 1.10  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.9  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.8  2004/03/09 09:31:41  ncq
-- - merged most form def tables into reference service schema
--
-- Revision 1.7  2004/03/08 17:04:23  ncq
-- - rewritten after discussion with Ian
--
-- Revision 1.6  2004/03/07 22:42:08  ncq
-- - just some cleanup
--
-- Revision 1.5  2004/03/07 13:19:18  ihaywood
-- more work on forms
--
-- Revision 1.4  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.3  2003/01/01 13:36:56  ncq
-- - in queries: string constants must be quoted by ''s
--
-- Revision 1.2  2003/01/01 00:21:25  ncq
-- - added flag is_editable to form field definition
--
-- Revision 1.1  2003/01/01 00:15:06  ncq
-- - this imports cleanly for me, please comment
--
