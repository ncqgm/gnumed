-- structure of configuration database for gnumed
-- Copyrigth by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org

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

CREATE TABLE dbprofile (
    id SERIAL PRIMARY KEY,
    username CHAR(25) DEFAULT CURRENT_USER,
    pwd_encrypted TEXT,
    pwd_cryptalgo VARCHAR(60) DEFAULT 'rijndael'
);


COMMENT ON TABLE dbprofile IS
'user specific information of a specific database';

COMMENT ON COLUMN dbprofile.username IS
'user name of the current user on that particular database';

COMMENT ON COLUMN dbprofile.pwd_encrypted IS
'encrypted password of the user for that database, useful in that a master password can unlock all databases';

COMMENT ON COLUMN dbprofile.pwd_cryptalgo IS
'algorithm that was used for encrypting the database user password';

--=====================================================================

CREATE TABLE dbset (
    id SERIAL PRIMARY KEY,
    fk_db INT REFERENCES db NOT NULL,
    fk_dbprofile INT REFERENCES dbprofile NOT NULL
);

COMMENT ON TABLE dbset IS
'all information neccessary to log into a particular database';

COMMENT ON COLUMN dbset.fk_db IS
'foreign key referencing general database information';

COMMENT ON COLUMN dbset.fk_dbprofile IS
'foreign key referencing database related user profile information';

--=====================================================================

CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    username CHAR(25) DEFAULT CURRENT_USER,
    profile CHAR(25),
    demographica INT REFERENCES dbset DEFAULT NULL,
    geographica INT REFERENCES dbset DEFAULT NULL,
    ref_drug INT REFERENCES dbset DEFAULT NULL,
    ref_pateducation INT REFERENCES dbset DEFAULT NULL,
    ref_travelmedicine INT REFERENCES dbset DEFAULT NULL,
    ref_vaccination INT REFERENCES dbset DEFAULT NULL,
    transactions INT REFERENCES dbset DEFAULT NULL,
    progressnotes INT REFERENCES dbset DEFAULT NULL,
    imaging INT REFERENCES dbset DEFAULT NULL,
    pathresults INT REFERENCES dbset DEFAULT NULL,
    blobs INT REFERENCES dbset DEFAULT NULL
);

COMMENT ON TABLE config IS
'minimal gnumed database configuration information';

COMMENT ON COLUMN config.username IS
'user name as used within the gnumed system';

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

COMMENT ON COLUMN config.demographica IS
'demographic information database server';




