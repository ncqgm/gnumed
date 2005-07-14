-- =============================================
-- project: GNUmed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmSchemaRevision.sql,v $
-- $Id: gmSchemaRevision.sql,v 1.13 2005-07-14 21:29:40 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- import this file into any database you create and
-- add the revision of your schema files into the revision table,
-- this will allow for a simplistic manual database schema revision control,
-- that may come in handy when debugging live production databases,

-- TODO: add log_script_insertion(text, text, boolean)

-- for your convenience, just copy/paste the following lines:
-- (don't worry about the filename/revision that's in there, it will
--  be replaced automagically with the proper data by "cvs commit")

-- do simple schema revision tracking
-- select log_script_insertion('$RCSfile: gmSchemaRevision.sql,v $', '$Revision: 1.13 $', True/False);

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
	is_core boolean
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
comment on column gm_schema_revision.is_core is
	'whether this script is to be included in calculating
	 the identity hash of this database, thereby one can
	 flexibly ignore test data scripts and such which do
	 not really affect the schema layout itself';
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
	 in the function below';

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

-- ---------------------------------------------
create function calc_db_identity_hash() returns text as '
declare
	_row record;
	_total text;
	_hash text;
begin
	_total := '''';
	for _row in select filename, version from gm_schema_revision where is_core order by filename, version loop
		_total := _total || _row.filename || _row.version;
	end loop;
	select into _hash md5(_total);
	return _hash;
end;' language 'plpgsql';

comment on function calc_db_identity_hash() is
	'this is how we calculate the hash:
	 - select relevant script rows (is_core is True)
	 - order them by file name/revision such that
	   real order of insertion is insignificant
	 - concatenate name + version + name + version + ...
	 - calculate md5 hash of concatenated string
	   (md5 because it is built in)';

-- ---------------------------------------------
create function log_script_insertion(text, text, boolean) returns text as '
declare
	_filename alias for $1;
	_version alias for $2;
	_is_core alias for $3;
	_hash text;
begin
	delete from gm_schema_revision where filename = _filename;
	insert into gm_schema_revision (filename, version, is_core) values (
		_filename,
		_version,
		_is_core
	);
	select into _hash calc_db_identity_hash();
	delete from gm_database_revision;
	insert into gm_database_revision (identity_hash) values (_hash);
	return _hash;
end;' language 'plpgsql';

-- =============================================
GRANT SELECT on
	gm_schema_revision
	, gm_database_revision
	, gm_client_db_match
TO group "gm-public";

-- =============================================
-- $Log: gmSchemaRevision.sql,v $
-- Revision 1.13  2005-07-14 21:29:40  ncq
-- - add database revision tracking by md5 hash over gm_schema_revision
-- - enhance gm_schema_revision with is_core to allow for easy ignoring of non-schema-relevant skripts
-- - documentation, cleanup
-- - gm_client_db_match lookup table
-- - convenience functions log_script_insertion(), calc_db_identity_hash()
--
-- Revision 1.12  2005/03/01 20:38:19  ncq
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
