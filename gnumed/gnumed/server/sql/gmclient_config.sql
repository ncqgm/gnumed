-- ============================================================================
-- Tables for client-side configuration, storing options for the various users
-- tables to allow configration options for client to be storing
--remotely. 
-- tables contain metdata to allow client to construct configuration
-- dialogues on the fly
-- author: Ian Haywood

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1


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
       ancestor INTEGER, --How can a table reference itself? REFERENCES config_desc (id), -- default inherited from this config
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
