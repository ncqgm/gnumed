-- project: GNUMed

-- author: Horst Herb, Ian Haywood, Karsten Hilbert
-- copyright: authors
-- license: GPL (details at http://gnu.org)

-- droppable components of gmGIS schema

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-GIS-views.sql,v $
-- $Revision: 1.9 $
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
	adr.addendum as street2
from
	address adr,
	state s,
	urb,
	street str
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
	lp2a.id_identity as id,
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
	lnk_person2address lp2a
where
	adr.id_street = str.id
		and
	str.id_urb = urb.id
		and
	urb.id_state = s.id
		and
	lp2a.id_address = adr.id
		and
	lp2a.id_type = 1; -- home address


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

-- ====================================================
\unset ON_ERROR_STOP
drop rule insert_address on v_basic_address;
drop rule delete_address on v_basic_address;
drop rule update_address on v_basic_address;
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
\unset ON_ERROR_STOP
drop view v_zip2street;
\set ON_ERROR_STOP 1

create view v_zip2street as
	select
		coalesce (str.postcode, urb.postcode) as postcode,
		str.name as street,
		stt.name as state,
		stt.code as code_state,
		urb.name as urb,
		c.name as country,
		stt.country as code_country
	from
		street str,
		urb,
		state stt,
		country c
	where
		str.postcode is not null
			and
		str.id_urb = urb.id
			and
		urb.id_state = stt.id
			and
		stt.country = c.code
;

comment on view v_zip2street is
	'list known data for streets that have a zip code';

-- ===================================================================
\unset ON_ERROR_STOP
drop view v_zip2urb;
\set ON_ERROR_STOP 1

create view v_zip2urb as
	select
		urb.postcode as postcode,
		urb.name as urb,
		stt.name as state,
		stt.code as code_state,
		_(c.name) as country,
		stt.country as code_country
	from
		urb,
		state stt,
		country c
	where
		urb.postcode is not null
			and
		urb.id_state = stt.id
			and
		stt.country = c.code
;

comment on view v_zip2urb is
	'list known data for urbs that have a zip code';

-- ===================================================================
\unset ON_ERROR_STOP
drop view v_uniq_zipped_urbs;
\set ON_ERROR_STOP 1

create view v_uniq_zipped_urbs as
	-- all the cities that
	select
		urb.postcode as postcode,
		urb.name as name,
		stt.name as state,
		stt.code as code_state,
		_(c.name) as country,
		stt.country as code_country
	from
		urb,
		state stt,
		country c
	where
		-- have a zip code
		urb.postcode is not null
			and
		-- are not found in street with this zip code
		not exists(
			select 1 from
				v_zip2street vz2str,
				urb
			where
				vz2str.postcode = urb.postcode
					and
				vz2str.urb = urb.name
			) and
		urb.id_state = stt.id
			and
		stt.country = c.code
;

comment on view v_uniq_zipped_urbs is
	'convenience view that selects those urbs which
	 - have a zip code
	 - are not referenced in street with that zip code';

-- ===================================================================
\unset ON_ERROR_STOP
drop view v_zip2data;
\set ON_ERROR_STOP 1

create view v_zip2data as
	select
		vz2s.postcode as zip,
		vz2s.street,
		vz2s.urb,
		vz2s.state,
		vz2s.code_state,
		vz2s.country,
		vz2s.code_country
	from v_zip2street vz2s
		union
	select
		vuzu.postcode as zip,
		null as street,
		vuzu.name as urb,
		vuzu.state,
		vuzu.code_state,
		vuzu.country,
		vuzu.code_country
	from
		v_uniq_zipped_urbs vuzu
;

comment on view v_zip2data is
	'aggregates all known data per zip code';

GRANT select ON
	v_basic_address,
	v_home_address,
	v_zip2street,
	v_zip2urb,
	v_zip2data
TO GROUP "gm-doctors";

GRANT select, delete, insert, update ON
	v_basic_address
TO GROUP "_gm-doctors";


-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-GIS-views.sql,v $', '$Revision: 1.9 $');

-- ===================================================================
-- $Log: gmDemographics-GIS-views.sql,v $
-- Revision 1.9  2004-04-10 01:48:31  ihaywood
-- can generate referral letters, output to xdvi at present
--
-- Revision 1.8  2004/01/05 00:45:41  ncq
-- - drop rule wants relation name
--
-- Revision 1.7  2003/12/29 15:33:43  uid66147
-- - translate country.name in views
--
-- Revision 1.6  2003/09/21 06:54:13  ihaywood
-- sane permissions
--
-- Revision 1.5  2003/08/10 15:18:22  ncq
-- - eventually make the zip2data view work with help from Mike Mascari (pgsql-general)
--
-- Revision 1.4  2003/08/10 01:26:50  ncq
-- - make v_zip2data compile again
--
-- Revision 1.3  2003/08/10 01:07:46  ncq
-- - adapt to lnk_a2b table naming plan
-- - add v_zip2... views
--
-- Revision 1.2  2003/08/02 13:15:42  ncq
-- - better table aliases in complex queries
-- - a few more audit tables
--
-- Revision 1.1  2003/08/02 10:41:29  ncq
-- - rearranging files for clarity as to services/schemata
--
