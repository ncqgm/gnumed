-- structure of configuration database for gnumed
-- Copyrigth by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- last changes: 26.10.2001 hherb drastic simplification of entities and relationships

--=====================================================================

CREATE TABLE db (
    id SERIAL PRIMARY KEY,
    name CHAR(25),
    port INT DEFAULT 5432,
    host VARCHAR(255)DEFAULT 'localhost'
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

CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    profile CHAR(25) DEFAULT 'default',
    username CHAR(25) DEFAULT CURRENT_USER,
    crypt_pwd varchar(255) DEFAULT NULL,
    crypt_algo varchar(255) DEFAULT 'RIJNDAEL',
    pwd_hash varchar(255) DEFAULT NULL,
    hash_algo varchar(255) DEFAULT 'RIPEMD160',
    demographica INT REFERENCES db DEFAULT NULL,
    geographica INT REFERENCES db DEFAULT NULL,
    ref_drug INT REFERENCES db DEFAULT NULL,
    ref_pateducation INT REFERENCES db DEFAULT NULL,
    ref_travelmedicine INT REFERENCES db DEFAULT NULL,
    ref_vaccination INT REFERENCES db DEFAULT NULL,
    transactions INT REFERENCES db DEFAULT NULL,
    progressnotes INT REFERENCES db DEFAULT NULL,
    imaging INT REFERENCES db DEFAULT NULL,
    pathresults INT REFERENCES db DEFAULT NULL,
    blobs INT REFERENCES db DEFAULT NULL
);

COMMENT ON TABLE config IS
'minimal gnumed database configuration information';

COMMENT ON COLUMN config.profile IS
'allows multiple profiles per user / pseudo user';

COMMENT ON COLUMN config.username IS
'user name as used within the gnumed system';

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

COMMENT ON COLUMN config.demographica IS
'demographic information database server';

COMMENT ON COLUMN config.geographica IS
'geographic information database server';

COMMENT ON COLUMN config.ref_drug IS
'drug related information database server';

COMMENT ON COLUMN config.ref_pateducation IS
'patient education information related database server';

COMMENT ON COLUMN config.transactions IS
'database server responsible for allocating transaction IDs';






