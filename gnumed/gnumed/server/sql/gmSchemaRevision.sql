-- project: GnuMed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmSchemaRevision.sql,v $
-- $Revision: 1.2 $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- include this file in your psql script schema definition files,
-- after that add the revision of your file into the revision table,
-- this will allow for a simplistic manual database schema revision control,
-- that may come in handy when debugging live production databases,

-- for your convenience, just copy/paste the following three lines:
-- (don't worry about the filename/revision that's in there, it will
--  automagically be replaced with the proper data by "cvs commit")

-- do simple schema revision tracking
-- \i gmSchemaRevision.sql
-- INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmSchemaRevision.sql,v $', '$Revision: 1.2 $')

-- =============================================
\unset ON_ERROR_STOP
create table schema_revision(
	filename varchar(100),
	version varchar(30)
);
\set ON_ERROR_STOP 1

-- =============================================
-- $Log: gmSchemaRevision.sql,v $
-- Revision 1.2  2002-11-16 00:25:59  ncq
-- - added some clarification
--
-- Revision 1.1  2002/11/16 00:23:20  ncq
-- - provisions for simple database schema revision tracking
-- - read the source for instructions
--
