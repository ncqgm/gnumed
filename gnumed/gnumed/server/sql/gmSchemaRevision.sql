-- project: GnuMed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmSchemaRevision.sql,v $
-- $Revision: 1.12 $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- import this file into any database you create and
-- add the revision of your schema files into the revision table,
-- this will allow for a simplistic manual database schema revision control,
-- that may come in handy when debugging live production databases,

-- for your convenience, just copy/paste the following lines:
-- (don't worry about the filename/revision that's in there, it will
--  be replaced automagically with the proper data by "cvs commit")

-- do simple schema revision tracking
-- INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmSchemaRevision.sql,v $', '$Revision: 1.12 $');

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table gm_schema_revision (
	filename text,
	version text,
	imported timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
	unique (filename, version)
);

-- =============================================
GRANT SELECT on
	gm_schema_revision
TO group "gm-public";

-- =============================================
-- $Log: gmSchemaRevision.sql,v $
-- Revision 1.12  2005-03-01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.11  2003/06/10 08:56:59  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.10  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.9  2003/01/20 09:15:30  ncq
-- - unique (file, version)
--
-- Revision 1.8  2003/01/17 00:41:33  ncq
-- - grant select rights to all
--
-- Revision 1.7  2003/01/02 01:25:23  ncq
-- - GnuMed internal tables should be named gm_*
--
-- Revision 1.6  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.5  2002/11/17 08:24:55  ncq
-- - store timestamp not just date
--
-- Revision 1.4  2002/11/17 08:22:44  ncq
-- - forgot DEFAULT
--
-- Revision 1.3  2002/11/17 08:20:15  ncq
-- - added timestamp field
--
-- Revision 1.2  2002/11/16 00:25:59  ncq
-- - added some clarification
--
-- Revision 1.1  2002/11/16 00:23:20  ncq
-- - provisions for simple database schema revision tracking
-- - read the source for instructions
--
