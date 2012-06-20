-- =============================================
-- project: GNUmed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmSchemaRevision.sql,v $
-- $Id: gmSchemaRevision.sql,v 1.15 2005-09-19 16:22:12 ncq Exp $
-- license: GPL v2 or later
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
-- select log_script_insertion('$RCSfile: gmSchemaRevision.sql,v $', '$Revision: 1.15 $');

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table gm_schema_revision (
	pk serial primary key,		-- not *really* necessary
	filename text
		not null,
	version text
		not null,
	imported timestamp with time zone
		not null
		DEFAULT CURRENT_TIMESTAMP,
	unique (filename, version)
);

comment on table gm_schema_revision is
	'this table holds the revisions of all SQL scripts ever
	 inserted into this database, the values are preferably
	 provided by CVS tags in the scripts themselves, see above
	 for a convenient way to do that';
comment on column gm_schema_revision.filename is
	'the name of the script, handled most easily by CVS via "RCSfile"';
comment on column gm_schema_revision.version is
	'the version of the script, handled most easily by CVS via "Revision"';
comment on column gm_schema_revision.imported is
	'when this script was imported, mainly for debugging';

-- ---------------------------------------------
create table gm_database_revision (
	pk serial primary key,		-- not *really* necessary
	single_row_enforcer boolean
		unique
		default True
		check (single_row_enforcer is True),
	identity_hash text
		not null
);

comment on table gm_database_revision is
	'this table holds the database revision against
	 which clients can match their expectations,
	 the algorithm to calculate the hash is found
	 in the function calc_db_identity_hash()';

-- ---------------------------------------------
create table gm_client_db_match (
	pk serial primary key,		-- not *really* necessary
	client_type text
		not null,
	client_version text
		not null,
	db_identity_hash text
		not null,
	unique (client_version, client_type, db_identity_hash)
);

comment on table gm_client_db_match is
	'allows lookup of whether a given client version
	 can work with a particular database revision';
comment on column gm_client_db_match.client_type is
	'the type of client this row refers to';
comment on column gm_client_db_match.client_version is
	'the version of the client this row refers to';
comment on column gm_client_db_match.db_identity_hash is
	'the identity_hash of a database revision that
	 the client version can work with';

-- =============================================
