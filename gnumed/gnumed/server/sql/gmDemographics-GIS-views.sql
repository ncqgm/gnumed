-- project: GNUMed

-- author: Horst Herb, Ian Haywood, Karsten Hilbert
-- copyright: authors
-- license: GPL (details at http://gnu.org)

-- droppable components of gmGIS schema

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-GIS-views.sql,v $
-- $Revision: 1.2 $
-- ###################################################################
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- if you suffer from performance problems when selecting from this view,
-- implement it as a real table and create rules / triggers for insert,
-- update and delete that will update the underlying tables accordingly
create view v_basic_address as
select
	adr.id as addr_id,
	s.country as country,
	s.code as state,
	coalesce (str.postcode, urb.postcode) as postcode,
	urb.name as city,
	adr.number as number,
	str.name as street,
	adr.addendum as street2,
	typ.name as address_at
from
	address adr,
	state s,
	urb,
	street str,
	address_type typ
where
	adr.id_street = str.id
		and
	str.id_urb = urb.id
		and
	urb.id_state = s.id;

-- added IH 8/3/02
-- insert, delete, and update rules on this table
-- problem: the street table had better contain the street.
-- solution: function to auto-create street records on demand.

create view v_home_address as
select
	pa.id_identity as id,
	s.country as country,
	s.code as state,
	coalesce (str.postcode, urb.postcode) as postcode,
	urb.name as city,
	adr.number as number,
	str.name as street,
	adr.addendum as street2
from
	address adr,
	state s,
	urb,
	street str,
	person_addresses pa
where
	adr.id_street = str.id
		and
	str.id_urb = urb.id
		and
	urb.id_state = s.id
		and
	pa.id_address = adr.id
		and
	pa.id_type = 1; -- home address


-- ===================================================================
-- finds the state for a given postcode in a given country
\unset ON_ERROR_STOP
DROP function find_state(text, text);
DROP function find_street(text, integer);
\set ON_ERROR_STOP 1
create function find_state (text, text) RETURNS text AS '
DECLARE
	pcode ALIAS FOR $1;	-- post code
	ccode ALIAS FOR $2;	-- country code
	s RECORD;
	retval text := NULL;
BEGIN
	SELECT INTO s * FROM state WHERE
		id = (SELECT id_state from urb where postcode like pcode||''%'' limit 1)
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
create function find_street (text, integer) RETURNS integer AS '
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
create function find_or_create_state(text, text) RETURNS integer AS '
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
create function find_urb (text, text, text, text) RETURNS integer AS '
DECLARE
	u_country ALIAS FOR $1;
	u_state ALIAS FOR $2;
	u_postcode ALIAS FOR $3;
	u_name ALIAS FOR $4;
	u RECORD;
	state_code INTEGER;
BEGIN
	state_code = find_or_create_state(u_state, u_country);
	SELECT INTO u *
	FROM urb
	WHERE
		id_state = state_code
			AND
		postcode = u_postcode
			AND
		name = u_name;

	IF FOUND THEN
		RETURN u.id;
	ELSE
		INSERT INTO urb (id_state, postcode, name)
		VALUES (state_code, u_postcode, u_name);
		RETURN currval (''urb_id_seq'');
	END IF;
END;' language 'plpgsql';


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\unset ON_ERROR_STOP
drop rule insert_address;
drop rule delete_address;
drop rule update_address;
\set ON_ERROR_STOP 1

CREATE RULE insert_address AS ON INSERT TO v_basic_address DO INSTEAD
	INSERT INTO address (id_street, number, addendum)
    VALUES (
		find_street(
			NEW.street,
			find_urb(NEW.country, NEW.state, NEW.postcode, NEW.city)
		),
		NEW.number,
		NEW.street2
	);

CREATE RULE delete_address AS ON DELETE TO v_basic_address DO INSTEAD
	DELETE FROM address
	WHERE address.id = OLD.addr_id
;

-- updates the basic address data as identified by it's unique id
CREATE RULE update_address AS ON UPDATE TO v_basic_address DO INSTEAD
	UPDATE
		address
	SET
		number = NEW.number,
		addendum = NEW.street2,
		id_street = find_street (
			NEW.street,
			(SELECT urb.id
			 FROM urb, state
			 WHERE
				urb.name = NEW.city AND
				urb.postcode = NEW.postcode AND
				urb.id_state = state.id AND
				state.code = NEW.state AND
				state.country = NEW.country
			)
		)
	WHERE
		address.id=OLD.addr_id
;

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-GIS-views.sql,v $', '$Revision: 1.2 $');

-- ===================================================================
-- $Log: gmDemographics-GIS-views.sql,v $
-- Revision 1.2  2003-08-02 13:15:42  ncq
-- - better table aliases in complex queries
-- - a few more audit tables
--
-- Revision 1.1  2003/08/02 10:41:29  ncq
-- - rearranging files for clarity as to services/schemata
--
