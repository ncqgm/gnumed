--=====================================================================
-- GnuMed distributed database configuration tables

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmconfiguration.sql,v $
-- $Revision: 1.18 $

-- structure of configuration database for GnuMed
-- neccessary to allow for distributed servers
-- Copyright by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org

-- last changes: 26.10.2001 hherb drastic simplification of entities and relationships
-- introduction of the new services

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--=====================================================================
CREATE TABLE db (
    id SERIAL PRIMARY KEY,
    name CHAR(35),
    port INT DEFAULT 5432,
    host VARCHAR(255)DEFAULT 'localhost',
    opt varchar(255) DEFAULT '',
    tty varchar(255) DEFAULT ''
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

-- this service may be used for external audit trails and replication issues
INSERT INTO distributed_db(name) values('transactions');

-- this service contains all persoon and address related tables
INSERT INTO distributed_db(name) values('personalia');

-- this service contains patient's medical histories
INSERT INTO distributed_db(name) values('historica');

-- this service stores external downloadable results such as pathology
INSERT INTO distributed_db(name) values('extresults');

-- this service contains all correspondence (letters, emails)
INSERT INTO distributed_db(name) values('correspondence');

-- this service provides all pharmaceutical information
INSERT INTO distributed_db(name) values('pharmaceutica');

-- this service provides "external" reead only information such as coding (ICD)
-- and patient education material
INSERT INTO distributed_db(name) values('reference');

-- this service takes care of large (>= 2MB )binary objects
INSERT INTO distributed_db(name) values('blobs');

-- this services provides all tables for accounting purposes
INSERT INTO distributed_db(name) values('accounting');

-- this servicecontains office related tables such as rosters and waiting room
INSERT INTO distributed_db(name) values('office');

-- this service allows to manage GnuMed client modules
INSERT INTO distributed_db(name) values('modules');

--=====================================================
CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    profile CHAR(25) DEFAULT 'default',
    username CHAR(25) DEFAULT CURRENT_USER,
    ddb INT REFERENCES distributed_db DEFAULT NULL,
    db INT REFERENCES db,
    crypt_pwd varchar(255) DEFAULT NULL,
    crypt_algo varchar(255) DEFAULT NULL,
    pwd_hash varchar(255) DEFAULT NULL,
    hash_algo varchar(255) DEFAULT NULL
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

--=====================================================================
CREATE TABLE queries (
	id SERIAL PRIMARY KEY,
	name char(40),
	db INT REFERENCES DB,
	query text
);

-- ======================================================
create table cfg_type_enum (
	name varchar(20) unique
);

comment on table cfg_type_enum is
	'enumeration of config option data types';

INSERT INTO cfg_type_enum VALUES ('string');
INSERT INTO cfg_type_enum VALUES ('numeric');

-- ======================================================
create table cfg_template (
	id SERIAL PRIMARY KEY,
	name VARCHAR(20) NOT NULL DEFAULT 'must set this !',
	type VARCHAR (20) references cfg_type_enum (name),
	cfg_group VARCHAR (20) not null default 'default',
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

	id_template INTEGER REFERENCES cfg_template (id),
	owner varchar (30) not null default CURRENT_USER,
	machine VARCHAR (40) not null default 'default',
	cookie VARCHAR (40) not null default 'default'
);

comment on table cfg_item is
	'this table holds all "instances" of cfg_template';
comment on column cfg_item.id_template is
	'this points to the class of this option, think of this as a base object, this also defines the data type';
comment on column cfg_item.owner is
	'the database level user this option belongs to; this is the "role" of the user from the perspective of the database; can be "default" at the application level to indicate that it does not care';
comment on column cfg_item.machine is
	'the logical workplace this option pertains to; can be a hostname but should be a logical rather than a physical identifier, machines get moved, workplaces do not; kind of like a "role" for the machine; associate this with a physical machine through a local config file or environment variable; can be "default" if we do not care';
comment on column cfg_item.cookie is
	'an arbitrary, opaque entity the client code can use to associate this config item with even finer grained context; could be the pertinent patient ID for patient specific options; can default to "default"';

-- ======================================================
create table cfg_string (
	id_item integer references cfg_item (id),
	value text not null
);

-- ======================================================
create table cfg_numeric (
	id_item integer references cfg_item (id),
	value numeric not null
);

--=====================================================================
GRANT SELECT ON
	db,
	distributed_db,
	config,
	cfg_type_enum,
	cfg_template,
	cfg_item,
	cfg_string,
	cfg_numeric
TO GROUP "gm-public";

GRANT select, insert, update, delete on
	cfg_type_enum,
	cfg_template,
	cfg_item,
	cfg_string,
	cfg_numeric
to group "_gm-doctors";
-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmconfiguration.sql,v $', '$Revision: 1.18 $')

--=====================================================================
-- $Log: gmconfiguration.sql,v $
-- Revision 1.18  2002-11-28 11:53:44  ncq
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
