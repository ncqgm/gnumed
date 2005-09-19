--=====================================================================
-- GnuMed distributed database configuration tables

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmconfiguration.sql,v $
-- $Revision: 1.37 $

-- structure of configuration database for GnuMed
-- neccessary to allow for distributed servers

-- Copyright by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--=====================================================================
CREATE TABLE db (
    id SERIAL PRIMARY KEY,
    name CHAR(35),
    port INT DEFAULT 5432,
    host text DEFAULT 'localhost',
    opt text DEFAULT '',
    tty text DEFAULT ''
);

-- the database with id == 0 is the "default" database

COMMENT ON TABLE db IS
	'information on where to find the databases known to GnuMed';

COMMENT ON COLUMN db.name IS
	'name of the database';

COMMENT ON COLUMN db.port IS
	'port number of the server hosting the database';

COMMENT ON COLUMN db.host IS
	'host name or IP number of the server hosting the database';

--=====================================================================
CREATE TABLE distributed_db (
	id SERIAL PRIMARY KEY,
	name char(35)
);

COMMENT ON TABLE distributed_db IS
	'Enumerate all known GnuMed service names. Naming new services needs approval by GnuMed administrators !';

-- i18N note to translators: do NOT change these values !!!

-- this service contains at least the basic GnuMed configuration
INSERT INTO distributed_db(name) values('default');

-- this service contains all person and address related tables
-- eg. demographic and identity data
INSERT INTO distributed_db(name) values('personalia');

-- this service contains patient's medical histories
INSERT INTO distributed_db(name) values('historica');

-- this service provides all pharmaceutical information
-- eg. drugref.org, mainly
INSERT INTO distributed_db(name) values('pharmaceutica');

-- this service provides "external" reead only information such
-- as coding (ICD) and patient education material
INSERT INTO distributed_db(name) values('reference');

-- this service takes care of large (>= 2MB )binary objects
INSERT INTO distributed_db(name) values('blobs');

-- this service holds all the administrative data for the
-- practice: forms queue, roster, waiting room, billing etc.
insert into distributed_db(name) values('administrivia');

--=====================================================
CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    profile CHAR(25) DEFAULT 'default',
    username CHAR(25) DEFAULT CURRENT_USER,
    ddb INT REFERENCES distributed_db DEFAULT NULL,
    db INT REFERENCES db,
    crypt_pwd text DEFAULT NULL,
    crypt_algo text DEFAULT NULL,
    pwd_hash text DEFAULT NULL,
    hash_algo text DEFAULT NULL
);

COMMENT ON TABLE config IS
	'maps a service name to a database location for a particular user, includes user credentials for that database';

COMMENT ON COLUMN config.profile IS
	'allows multiple profiles per user / pseudo user, one user may have different configuration profiles depending on role, need and location';

COMMENT ON COLUMN config.username IS
	'user name as used within the GnuMed system';

COMMENT ON COLUMN config.ddb IS
	'which GnuMed service are we mapping to a database here';

COMMENT ON COLUMN config.db IS
	'how to reach the database host for this service';

COMMENT ON COLUMN config.crypt_pwd IS
	'password for user and database, encrypted';

COMMENT ON COLUMN config.crypt_algo IS
	'encryption algorithm used for password encryption';

COMMENT ON COLUMN config.pwd_hash IS
	'hash of the unencrypted password';

COMMENT ON COLUMN config.hash_algo IS
	'algorithm used for password hashing';

-- ======================================================
-- generic program options storage space
-- ======================================================
create table cfg_type_enum (
	name text
		unique
		not null
);

comment on table cfg_type_enum is
	'enumeration of config option data types';

INSERT INTO cfg_type_enum VALUES ('string');
INSERT INTO cfg_type_enum VALUES ('numeric');
INSERT INTO cfg_type_enum VALUES ('str_array');
insert into cfg_type_enum values ('data');

-- ======================================================
create table cfg_template (
	id SERIAL PRIMARY KEY,
	name text NOT NULL DEFAULT 'must set this !',
	type text references cfg_type_enum (name),
	cfg_group text not null default 'xxxDEFAULTxxx',
	description TEXT NOT NULL DEFAULT 'programmer is an avid Camel Book Reader'
);

comment on table cfg_template is
	'meta definition of config items';
comment on column cfg_template.name is
	'the name of the option; this MUST be set to something meaningful';
comment on column cfg_template.type is
	'type of the value';
comment on column cfg_template.cfg_group is
	'just for logical grouping of options according to task sets to facilitate better config management';
comment on column cfg_template.description is
	'arbitrary description (user visible)';

-- ======================================================
create table cfg_item (
	id SERIAL PRIMARY KEY,
	id_template INTEGER
		not null
		references cfg_template (id),
	owner name
		not null
		default CURRENT_USER,
	workplace text
		not null
		default 'xxxDEFAULTxxx',
	cookie text
		not null
		default 'xxxDEFAULTxxx',
	unique (id_template, owner, workplace, cookie)
);

comment on table cfg_item is
	'this table holds all "instances" of cfg_template';
comment on column cfg_item.id_template is
	'this points to the class of this option, think of this as a base object, this also defines the data type';
comment on column cfg_item.owner is
	'the database level user this option belongs to; this
	 is the "role" of the user from the perspective of
	 the database; can be "default" at the application
	 level to indicate that it does not care';
comment on column cfg_item.workplace is
	'- the logical workplace this option pertains to
	 - can be a hostname but should be a logical rather
	   than a physical identifier as machines get moved,
	   workplaces do not, kind of like a "role" for the
	   machine
	 - associate this with a physical workplace through
	   a local config file or environment variable';
comment on column cfg_item.cookie is
	'an arbitrary, opaque entity the client code can use
	 to associate this config item with even finer grained
	 context; could be the pertinent patient ID for patient
	 specific options';

-- ======================================================
create table cfg_string (
	id_item integer
		not null
		references cfg_item(id)
		on update cascade
		on delete cascade,
	value text not null
);

-- ======================================================
create table cfg_numeric (
	id_item integer
		not null
		references cfg_item(id)
		on update cascade
		on delete cascade,
	value numeric not null
);

-- ======================================================
create table cfg_str_array (
	id_item integer
		not null
		references cfg_item(id)
		on update cascade
		on delete cascade,
	value text[] not null
);

-- ======================================================
create table cfg_data (
	id_item integer
		not null
		references cfg_item(id)
		on update cascade
		on delete cascade,
	value bytea
		not null
);

comment on table cfg_data is
	'stores opaque configuration data, either text or binary,
	 note that it will be difficult to share such options
	 among different types of clients';

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmconfiguration.sql,v $', '$Revision: 1.37 $');

--=====================================================================
-- $Log: gmconfiguration.sql,v $
-- Revision 1.37  2005-09-19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.36  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.35  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.34  2005/01/09 19:51:24  ncq
-- - cleanup, improved docs
-- - add cfg_data to store arbitrary binary config data
--
-- Revision 1.33  2004/09/06 22:15:07  ncq
-- - tighten constraints in cfg_item
--
-- Revision 1.32  2004/09/02 00:42:33  ncq
-- - add v_cfg_options
-- - move grants to volatile DDL file
--
-- Revision 1.31  2004/07/19 11:50:43  ncq
-- - cfg: what used to be called "machine" really is "workplace", so fix
--
-- Revision 1.30  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.29  2004/03/10 00:06:20  ncq
-- - remove stale service defs
--
-- Revision 1.28  2004/01/06 23:44:40  ncq
-- - __default__ -> xxxDEFAULTxxx
--
-- Revision 1.27  2003/10/27 13:54:05  ncq
-- - cleanup
--
-- Revision 1.26  2003/10/26 23:02:22  hinnef
-- - changed config param name length to 80
--
-- Revision 1.25  2003/07/27 22:01:48  ncq
-- - comment out unused service names
--
-- Revision 1.24  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.23  2003/02/04 12:22:53  ncq
-- - valid until in create user cannot do a sub-query :-(
-- - columns "owner" should really be of type "name" if defaulting to "CURRENT_USER"
-- - new functions set_curr_lang(*)
--
-- Revision 1.22  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.21  2003/01/05 10:07:15  ncq
-- - default "__default__"
-- - adjusted ACLs
--
-- Revision 1.20  2002/12/26 15:44:42  ncq
-- - added string array
--
-- Revision 1.19  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.18  2002/11/28 11:53:44  ncq
-- - added client configuration tables to work with database config library
-- - adjusted ACLs
--
-- Revision 1.17  2002/11/16 01:03:20  ncq
-- - add simple revision tracking
--
-- Revision 1.16  2002/11/12 17:04:10  ncq
-- - remove a ; in a '' since this currently foo-bars bootstrapping
--
-- Revision 1.15  2002/11/01 16:53:27  ncq
-- - still errors in here, darn it !
--
-- Revision 1.14  2002/11/01 16:35:38  ncq
-- - still some grant errors lurking
--
-- Revision 1.13  2002/11/01 16:11:07  ncq
-- - fixed grants, comments, quoting
--
-- Revision 1.12  2002/10/29 23:08:08  ncq
-- - some cleanup
-- - started work on GnuMed user/group ACL structure
--
-- Revision 1.11  2002/09/27 00:35:03  ncq
-- - janitorial work
-- - comments for clarification

-- last changes: 26.10.2001 hherb drastic simplification of entities and relationships
-- introduction of the new services
