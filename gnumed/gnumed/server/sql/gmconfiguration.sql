--=====================================================================
-- GnuMed distributed database configuration tables

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmconfiguration.sql,v $
-- $Revision: 1.15 $

-- structure of configuration database for GnuMed
-- neccessary to allow for distributed servers
-- Copyright by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org

-- last changes: 26.10.2001 hherb drastic simplification of entities and relationships
-- introduction of the new services
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
	'allows multiple profiles per user / pseudo user; one user may have different configuration profiles depending on role, need and location';

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
--=====================================================================
GRANT SELECT ON db, distributed_db, config TO GROUP "gm-public";

--=====================================================================
-- $Log: gmconfiguration.sql,v $
-- Revision 1.15  2002-11-01 16:53:27  ncq
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
