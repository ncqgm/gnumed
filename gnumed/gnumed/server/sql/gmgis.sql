-- project: GNUMed
-- database: GIS
-- purpose:  geographic information (mostly of type 'address')
-- author: hherb
-- copyright: Dr. Horst Herb, horst@hherb.com
-- license: GPL (details at http://gnu.org)
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmgis.sql,v $
-- $Revision: 1.27 $
-- changelog:
-- 17.11.2001:  (hherb) first useable version
-- 04.03.2002:  (hherb) address_type bug in view basic_addess fixed
-- 04.03.2002:  (hherb) table state constraint added
-- 08.03.2002:  (ihaywood) rules for v_basic_address, address_info altered
-- 30.03.2002:  (hherb) view basic_address renamed to v_basic_address
--               bugfix in rule update_address
--               bugfix in rule insert_address
-- 31.03.2002:  rules for v_basic_address rewritten, using id now
--               and supporting external reference counting
-- ###################################################################
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- any table that needs auditing MUST inherit audit_gis
-- A python script (gmhistorian.py) generates automatically all triggers
-- and tables neccessary to allow versioning and audit trail keeping of
-- these tables
create table audit_gis (
	audit_id serial primary key
);

COMMENT ON TABLE audit_gis IS
	'not for direct use - must be inherited by all auditable tables';

-- ===================================================================
-- country codes as per ISO 3166-1
-- no versioning / check sum neccessary, as this table
-- only uses original ISO data (= reference verifiable any time)
create table country (
	code char(2) unique primary key,
	name varchar(80) NOT NULL,
	deprecated date default NULL
);

COMMENT ON TABLE country IS
	'a countries name and international code';
COMMENT ON COLUMN country.code IS
	'international two character country code as per ISO 3166-1';
COMMENT ON COLUMN country.deprecated IS
	'date when this country ceased officially to exist (if applicable)';

-- Here come the ISO country codes ...
-- \copy country from 'iso-country-codes.txt'

-- ===================================================================
-- state codes. Any need for more than 3 characters?
-- yes, at least in Germany we have up to 6

create table state (
        id serial primary key,
        code char(10),
        country char(2) references country(code),
        name varchar(60),
        deprecated date,
        constraint nodupes UNIQUE (code, country)
) inherits (audit_gis);

COMMENT ON TABLE state IS
	'state codes (country specific)';
COMMENT ON COLUMN state.code IS
	'state code';
COMMENT ON COLUMN state.country IS
	'2 character ISO 3166-1 country code';
COMMENT ON COLUMN country.deprecated IS
	'date when this state ceased officially to exist (if applicable)';

-- ===================================================================
create table urb (
	id serial primary key,
	statecode int references state(id),
	postcode char(8),
	name varchar(60)
) inherits (audit_gis);

-- this does not work in the UK! Seperate postcodes for each street
-- same in Germany: postcodes can be valid for:
-- - several smaller urbs
-- - one urb
-- - several streets in one urb
-- - one street in one urb
-- - part of one street in one urb
-- Take that !  :-)

COMMENT ON TABLE urb IS
	'cities, towns, dwellings ...';
COMMENT ON COLUMN urb.statecode IS
	'reference to information about country and state';
COMMENT ON COLUMN urb.postcode IS
	'the postcode (if applicable';
COMMENT ON COLUMN urb.name IS
	'the name of the city/town/dwelling';

-- ===================================================================
create table street (
	id serial primary key,
	id_urb integer references urb not null,
	name varchar(60),
	postcode char (10)
) inherits (audit_gis);
 -- for UK (or similar) postcodes

COMMENT ON TABLE street IS
	'street names, specific for distinct "urbs"';
COMMENT ON COLUMN street.id_urb IS
	'reference to information postcode, city, country and state';
COMMENT ON COLUMN street.name IS
	'name of this street';
COMMENT ON COLUMN street.postcode IS
	'postcode for systems (such as UK Royal Mail) which specify the street.';

-- ===================================================================
create table address_type (
	id serial primary key,
	name char(10) NOT NULL
) inherits (audit_gis);

 -- do not alter the id of home !
INSERT INTO address_type(id, name) values(1,'home');
INSERT INTO address_type(id, name) values(2,'work');
INSERT INTO address_type(id, name) values(3,'parents');
INSERT INTO address_type(id, name) values(4,'holidays');
INSERT INTO address_type(id, name) values(5,'temporary');

-- ===================================================================
create table address (
	id serial primary key,
	street int references street(id),
	number char(10),
	addendum text
) inherits (audit_gis);

-- ===================================================================
-- Other databases may reference to an address stored in this table.
-- As Postgres does not allow (yet) cross database queries, we use
-- external reference tables containing "external reference" counters
-- in order to preserve referential integrity
-- (no address shall be deleted as long as there is an external object
-- referencing this address)
create table address_external_ref (
	id int references address primary key,
	refcounter int default 0
);

-- ===================================================================
create table identities_addresses (
	id serial primary key,
	id_identity integer references identity,
	id_address integer references address,
	id_type int references address_type default 1,
	address_source varchar(30)
) inherits (audit_identity);

COMMENT ON TABLE identities_addresses IS
	'a many-to-many pivot table linking addresses to identities';
COMMENT ON COLUMN identities_addresses.id_identity IS
	'identity to whom the address belongs';
COMMENT ON COLUMN identities_addresses.id_address IS
	'address belonging to this identity';
COMMENT ON COLUMN identities_addresses.id_type IS
	'type of this address (like home, work, parents, holidays ...)';

-- ===================================================================
-- if you suffer from performance problems when selecting from this view,
-- implement it as a real table and create rules / triggers for insert,
-- update and delete that will update the underlying tables accordingly
create view v_basic_address as
select
	a.id as addr_id,
	s.country as country,
	s.code as state,
	u.postcode as postcode,
	u.name as city,
	a.number as number,
	str.name as street,
	a.addendum as street2,
	t.name as address_at
from
	address a,
	state s,
	urb u,
	street str,
	address_type t
where
	a.street = str.id
		and
	str.id_urb = u.id
		and
	u.statecode = s.id;

-- added IH 8/3/02
-- insert, delete, and update rules on this table
-- problem: the street table had better contain the street.
-- solution: function to auto-create street records on demand.

-- ===================================================================
-- finds the state for a given postcode in a given country
\unset ON_ERROR_STOP
DROP function find_state(text, text);
DROP function find_street(text, integer);
\set ON_ERROR_STOP 1
CREATE FUNCTION find_state (text, text) RETURNS text AS '
DECLARE
	pcode ALIAS FOR $1;	-- post code
	ccode ALIAS FOR $2;	-- country code
	s RECORD;
	retval text := NULL;
BEGIN
	SELECT INTO s * FROM state WHERE
		id = (SELECT statecode from urb where postcode like pcode||''%'' limit 1)
			AND
		country=ccode;
	IF FOUND THEN
		retval := s.code;
	END IF;
	RETURN retval;
END;' LANGUAGE 'plpgsql';

-- ===================================================================
-- This function returns the id of street, BUT if the street does not
-- exist, it is created.
CREATE FUNCTION find_street (text, integer) RETURNS integer AS '
DECLARE
	s_name ALIAS FOR $1;
	s_id_urb ALIAS FOR $2;
	s RECORD;
BEGIN
	SELECT INTO s * FROM street WHERE
		name = s_name
			AND
		id_urb = s_id_urb;
	IF FOUND THEN
		RETURN s.id;
	ELSE
		INSERT INTO street (id_urb, name) VALUES (s_id_urb, s_name);
		RETURN currval (''street_id_seq'');
	END IF;
END;' LANGUAGE 'plpgsql';


-- This function returns the id of a state, BUT if the state does not
-- exist, it is created.
\unset ON_ERROR_STOP
DROP function find_or_create_state(text, text);
\set ON_ERROR_STOP 1
CREATE FUNCTION find_or_create_state(text, text) RETURNS integer AS '
DECLARE
        s_code ALIAS FOR $1;
        s_country ALIAS FOR $2;
        s RECORD;
BEGIN
        SELECT INTO s * FROM state
	WHERE code = s_code
	AND country = s_country;
        IF FOUND THEN
           RETURN s.id;
        ELSE
           INSERT INTO state (code, country) VALUES (s_code, s_country);
           RETURN currval (''state_id_seq'');
        END IF;
END;' LANGUAGE 'plpgsql';



-- This function returns the id of urb, BUT if the urb does not
-- exist, it is created.
\unset ON_ERROR_STOP
DROP function find_urb(text, text, text, text);
\set ON_ERROR_STOP 1
CREATE FUNCTION find_urb (text, text, text, text) RETURNS integer AS '
DECLARE
        u_country ALIAS FOR $1;
        u_state ALIAS FOR $2;
	u_postcode ALIAS FOR $3;
        u_name ALIAS FOR $4;
        u RECORD;
	state_code INTEGER;
BEGIN
	state_code = find_or_create_state(u_state, u_country);
	SELECT INTO u * FROM urb
	WHERE statecode = statecode
	AND postcode = u_postcode
	AND name = u_name;

        IF FOUND THEN
           RETURN u.id;
        ELSE
           INSERT INTO urb (statecode, postcode, name)
	   VALUES (state_code, u_postcode, u_name);
           RETURN currval (''urb_id_seq'');
        END IF;
END;' LANGUAGE 'plpgsql';


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

\unset ON_ERROR_STOP
DROP rule insert_address;
\set ON_ERROR_STOP 1
CREATE RULE insert_address AS ON INSERT TO v_basic_address DO INSTEAD
        INSERT INTO address (street, number, addendum)
        VALUES (find_street (NEW.street, 
	                      find_urb(NEW.country, NEW.state, NEW.postcode, NEW.city)),
                NEW.number,
	        NEW.street2);

--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CREATE RULE delete_address AS ON DELETE TO v_basic_address DO INSTEAD
	DELETE FROM address
	WHERE address.id = OLD.addr_id;


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-- updates the basic address data as identified by it's unique id

CREATE RULE update_address AS ON UPDATE TO v_basic_address DO INSTEAD
	UPDATE address SET
		number = NEW.number,
		addendum = NEW.street2,
		street = find_street (
			NEW.street,
			(SELECT urb.id FROM urb, state WHERE
				urb.name = NEW.city AND
				urb.postcode = NEW.postcode AND
				urb.statecode = state.id AND
				state.code = NEW.state AND
				state.country = NEW.country
			)
		)
		WHERE
			address.id=OLD.addr_id;

-- =============================================

-- the following table still needs a lot of work.
-- especially the GPS and map related information needs to be
-- normalized

-- added IH 8/3/02
-- table for street civilian type maps, i.e Melways
create table mapbook (
       id serial,
       name char (30)
);


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


-- table for co-ordinate systems, such at latitude-longitude
-- there are others, military, aviation and country-specific.
-- GPS handsets can display several.
create table coordinate (
      id serial,
      name varchar (30),
      scale float
);
      -- NOTE: this converts distances from the co-ordinate units to
      -- kilometres.
      -- theoretically this may be problematic with some systems due to the
      -- ellipsoid nature of the Earth, but in reality it is unlikely to matter

--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


create table address_info (
        address_id int references address(id),
        location point,
        id_coord integer references coordinate (id),
        mapref char(30),
        id_map integer references mapbook (id),
        howto_get_there text,
        comments text
) inherits (audit_gis);

-- this refers to a SQL point type. This would allow us to do
-- interesting queries, like, how many patients live within
-- 10kms of the clinic.

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmgis.sql,v $', '$Revision: 1.27 $');
