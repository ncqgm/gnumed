-- =============================================
-- GNUmed service discovery tables
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmServices.sql,v $
-- $Id: gmServices.sql,v 1.8 2005-09-19 16:38:51 ncq Exp $
-- license: GPL v2 or later
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
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmServices.sql,v $', '$Revision: 1.8 $');
