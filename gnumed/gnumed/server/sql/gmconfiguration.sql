-- structure of configuration database for gnumed
-- neccessary to allow for distributed servers
-- Copyrigth by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- last changes: 26.10.2001 hherb drastic simplification of entities and relationships

--=====================================================================

CREATE TABLE db (
    id SERIAL PRIMARY KEY,
    name CHAR(35),
    port INT DEFAULT 5432,
    host VARCHAR(255)DEFAULT 'localhost',
    opt varchar(255) DEFAULT '',
    tty varchar(255) DEFAULT ''
);

COMMENT ON TABLE db IS
'basic database information';

COMMENT ON COLUMN db.name IS
'name of the database';

COMMENT ON COLUMN db.port IS
'port number of the server hosting this database';

COMMENT ON COLUMN db.host IS
'host name or IP number of the server hosting this database';

--=====================================================================

CREATE TABLE distributed_db (
	id SERIAL PRIMARY KEY,
	name char(35)
);

COMMENT ON TABLE distributed_db IS
'Enumerates all possibly available distributed servers. Naming needs approval by gnumed administrators!';

-- !I18N note to translators: do NOT change these values !!!
INSERT INTO distributed_db(name) values('default');
INSERT INTO distributed_db(name) values('transactions');
INSERT INTO distributed_db(name) values('demographica');
INSERT INTO distributed_db(name) values('geographica');
INSERT INTO distributed_db(name) values('pharmaceutica');
INSERT INTO distributed_db(name) values('pathologica');
INSERT INTO distributed_db(name) values('radiologica');
INSERT INTO distributed_db(name) values('blobs');
INSERT INTO distributed_db(name) values('medicalhx');
INSERT INTO distributed_db(name) values('progressnotes');
INSERT INTO distributed_db(name) values('educativa');
INSERT INTO distributed_db(name) values('reference');
INSERT INTO distributed_db(name) values('modules');




CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    profile CHAR(25) DEFAULT 'default',
    username CHAR(25) DEFAULT CURRENT_USER,
    ddb INT REFERENCES distributed_db DEFAULT NULL,
    db INT REFERENCES db,
    crypt_pwd varchar(255) DEFAULT NULL,
    crypt_algo varchar(255) DEFAULT 'RIJNDAEL',
    pwd_hash varchar(255) DEFAULT NULL,
    hash_algo varchar(255) DEFAULT 'RIPEMD160'
);

COMMENT ON TABLE config IS
'minimal gnumed database configuration information';

COMMENT ON COLUMN config.profile IS
'allows multiple profiles per user / pseudo user';

COMMENT ON COLUMN config.username IS
'user name as used within the gnumed system';

COMMENT ON COLUMN config.ddb IS
'reference to one of the allowed distrbuted servers';

COMMENT ON COLUMN config.db IS
'reference to the implementation details of the distributed server';

COMMENT ON COLUMN config.crypt_pwd IS
'password for user and database, encrypted';

COMMENT ON COLUMN config.crypt_algo IS
'encryption algorithm used for password encryption';

COMMENT ON COLUMN config.pwd_hash IS
'hash of the unencrypted password';

COMMENT ON COLUMN config.hash_algo IS
'algorithm used for password hashing';

COMMENT ON COLUMN config.profile IS
'one user may have different configuration profiles depending on role, need and location';







