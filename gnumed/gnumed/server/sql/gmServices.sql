-- =============================================
-- GnuMed service discovery tables
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmServices.sql,v $
-- $Id: gmServices.sql,v 1.7 2005-07-14 21:31:42 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net
-- ---------------------------------------------
-- Import this file into any database you create and
-- insert data about which services it provides. This
-- is very useful for introspection and we all love that
-- from Python. It may also come in handy when debugging
-- live production databases.

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table gm_services (
	id serial primary key,
	name text unique,
	version text,
	created timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

comment on table gm_services is
	'this table lists all the services provided by this database';
comment on column gm_services.version is
	'not really used yet but will become useful in change management,
	 might take the form of a CVS release tag one day';

-- =============================================
\unset ON_ERROR_STOP
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmServices.sql,v $', '$Revision: 1.7 $', True);

-- =============================================
-- $Log: gmServices.sql,v $
-- Revision 1.7  2005-07-14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.6  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.5  2003/06/10 08:56:59  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.4  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.3  2003/01/22 23:09:47  ncq
-- - enable this to be imported more than once
--
-- Revision 1.2  2003/01/22 16:12:09  ncq
-- - gm_services.service_name -> gm_services.name
--
-- Revision 1.1  2003/01/02 01:20:31  ncq
-- - initial version
--
