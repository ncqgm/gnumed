-- structure of configuration database for gnumed
-- neccessary to allow for distributed servers
-- Copyrigth by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- last changes: 26.10.2001 hherb drastic simplification of entities and relationships
-- introduction ofg the new services

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

GRANT SELECT ON db TO PUBLIC;

--=====================================================================

CREATE TABLE distributed_db (
	id SERIAL PRIMARY KEY,
	name char(35)
);

COMMENT ON TABLE distributed_db IS
'Enumerates all possibly available distributed servers. Naming needs approval by gnumed administrators!';

-- !I18N note to translators: do NOT change these values !!!

-- this service contains at least the basic gnumed configuration
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

-- this service allows to manage gnumed client modules
INSERT INTO distributed_db(name) values('modules');

GRANT SELECT ON distributed_db TO PUBLIC;

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


CREATE TABLE queries (
	id SERIAL PRIMARY KEY,
	name char(40),
	db INT REFERENCES DB,
	query text
);

-- ==================================================================================
-- Tables for client-side configuration, storing options for the various users

CREATE TABLE config_type (
       id SERIAL PRIMARY KEY,
       name VARCHAR (20)
);

insert into config_type values (1, 'boolean');
insert into config_type values (2, 'range');
insert into config_type values (3, 'selection');
insert into config_type values (4, 'string');
insert into config_type values (5, 'colour');
insert into config_type values (6, 'font');


CREATE TABLE config_desc (
       id SERIAL,
       name VARCHAR (50) PRIMARY KEY,
       description TEXT,
       type INTEGER REFERENCES config_type (id), 
       ancestor INTEGER REFERENCES config_desc (id), -- default inherited from this config
       sys_def INTEGER, -- system default, never changed
       def INTEGER -- default 
);

insert into config_desc (name, type, sys_def, def) values ('main.notebook', 1, 1, 1);
insert into config_desc (name, type, ancestor) values ('notebook2', 1, 1);


-- values possible for a selection type variable
CREATE TABLE config_selection (
       id SERIAL PRIMARY KEY,
       desc_id INTEGER REFERENCES config_desc (id),
       value VARCHAR (100) NOT NULL
);


-- set ranges for range configs
CREATE TABLE config_range (
       id SERIAL PRIMARY KEY,
       desc_id INTEGER REFERENCES config_desc (id),
       minimum INTEGER NOT NULL,
       maximum INTEGER NOT NULL
);


-- values for specific users
CREATE TABLE config_user (
       id SERIAL PRIMARY KEY,
       desc_id INTEGER REFERENCES config_desc (id),
       value INTEGER, 
       user_name NAME DEFAULT current_user
);

CREATE FUNCTION insert_config () RETURNS OPAQUE AS '
    BEGIN
        IF EXISTS (SELECT 1 FROM config_user WHERE desc_id=NEW.desc_id AND user_name=current_user)
	THEN
	   RETURN NULL; -- nicely stop insertion of duplicate row
	ELSE
	   RETURN NEW;
	END IF;
    END;
' LANGUAGE 'plpgsql';

CREATE TRIGGER config_user_chk BEFORE INSERT ON config_user
    FOR EACH ROW EXECUTE PROCEDURE insert_config();


CREATE VIEW v_my_config AS 
SELECT desc1.id AS id, desc1.name AS name, desc1.type AS type,
COALESCE (
     (SELECT value FROM config_user WHERE desc_id=desc1.id AND user_name=current_user), 
     (SELECT value FROM config_user WHERE desc_id=desc1.ancestor AND user_name=current_user),
     def,
     (SELECT def FROM config_desc desc2 WHERE desc2.id=desc1.ancestor)) AS value
FROM config_desc desc1; 


CREATE RULE v_my_config_update AS ON UPDATE TO v_my_config 
DO INSTEAD
(
INSERT INTO config_user (desc_id, user_name) VALUES (NEW.id, current_user);
-- insert a new row of user config. If already exists, trigger will quietly suppress
UPDATE config_user SET value=NEW.value WHERE desc_id=NEW.id AND user_name=current_user;
);




--- lookup tables for colours, fonts, free strings
-- 'value' maps the to ID of these tables

CREATE TABLE config_colour (
       id SERIAL PRIMARY KEY,
       red INTEGER CHECK (red < 256 AND red >= 0) NOT NULL,
       green INTEGER CHECK (green < 256 AND green >= 0) NOT NULL,
       blue INTEGER CHECK (blue < 256 AND blue >=0) NOT NULL
);

CREATE TABLE config_string (
       id SERIAL PRIMARY KEY,
       nodelete BOOL,
       string TEXT NOT NULL
);

CREATE TABLE config_font (
       id SERIAL PRIMARY KEY,
       name varchar (100) NOT NULL
);         








