-- project: GNUMed

-- author: Horst Herb, Ian Haywood, Karsten Hilbert
-- copyright: authors
-- license: GPL (details at http://gnu.org)

-- droppable components of gmGIS schema

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-GIS-views.sql,v $
-- $Revision: 1.14 $
-- ###################################################################
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- if you suffer from performance problems when selecting from this view,
-- implement it as a real table 
create view v_basic_address as
select
	adr.id as id,
	s.country as country,
	s.code as state,
	coalesce (str.postcode, urb.postcode) as postcode,
	urb.name as city,
	adr.number as number,
	str.name as street,
	adr.addendum as addendum
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

-- ===================================================================
-- this function guarantees an ID for a given address, it will create
-- streets and addresses if required. It insists that the urb exists.
-- it will set street.postcode if urb.postcode is NULL.
\unset ON_ERROR_STOP
DROP function create_address (text, text, text, text, text);
\set ON_ERROR_STOP 1
create function create_address (text, text, text, text, text) RETURNS text AS '
DECLARE
	p_number alias for $1;
	p_addendum alias for $2;
	p_street alias for $3;
	city alias for $4;
	pcode alias for $5;
	r_addr address%ROWTYPE;
	r_urb urb%ROWTYPE;
	r_street street%ROWTYPE;
	street_id integer;
	
BEGIN
	SELECT INTO r_urb * FROM urb WHERE name ilike city;
	IF NOT FOUND THEN
		SELECT INTO r_urb * FROM urb WHERE postcode ilike pcode;
		IF NOT FOUND THEN
			RAISE EXCEPTION ''No such urb %'', city;
		END IF;
	END IF;
	IF r_urb.postcode IS NULL THEN		
		SELECT INTO r_street * FROM street WHERE
			name = street
				AND
			id_urb = r_urb.id
				AND
			postcode = pcode;
	ELSE
		SELECT INTO r_street * FROM street WHERE
			name = p_street
				AND
			id_urb = r_urb.id;
	END IF;
	IF FOUND THEN
		street_id := r_street.id;
	ELSE
		IF r_urb.postcode IS NULL THEN
			INSERT INTO street (id_urb, name, postcode) VALUES (r_urb.id, p_street, pcode);
		ELSE 
			INSERT INTO street (id_urb, name) VALUES (r_urb.id, p_street);
		END IF;
		street_id := currval (''street_id_seq'');
		INSERT INTO address (number, addendum, id_street) VALUES (p_number, p_addendum, street_id);
		RETURN currval (''address_id_seq'');
	END IF;
	SELECT INTO r_addr * FROM address WHERE
		number = p_number AND addendum = p_addendum AND id_street = street_id;
	IF FOUND THEN
		RETURN r_addr.id;
	ELSE
		INSERT INTO address (number, addendum, id_street) VALUES (p_number, p_addendum, street_id);
		RETURN currval (''address_id_seq'');
	END IF; 
END;' LANGUAGE 'plpgsql';

-- ===================================================================
\unset ON_ERROR_STOP
drop view v_zip2street;
\set ON_ERROR_STOP 1

create view v_zip2street as
	select
		coalesce (str.postcode, urb.postcode) as postcode,
		str.name as street,
		str.suburb as suburb,
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
		-- are not found in "street" with this zip code
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
	'convenience view that selects urbs which:
	 - have a zip code
	 - are not referenced in table "street" with that zip code';

-- ===================================================================
\unset ON_ERROR_STOP
drop view v_zip2data;
\set ON_ERROR_STOP 1

create view v_zip2data as
	select
		vz2s.postcode as zip,
		vz2s.street,
		vz2s.suburb,
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
		null as suburb,
		vuzu.name as urb,
		vuzu.state,
		vuzu.code_state,
		vuzu.country,
		vuzu.code_country
	from
		v_uniq_zipped_urbs vuzu
;

comment on view v_zip2data is
	'aggregates nearly all known data per zip code';

-- ===================================================================
GRANT select ON
	v_basic_address,
	v_zip2street,
	v_zip2urb,
	v_zip2data
TO GROUP "gm-doctors";

GRANT select, delete, insert, update ON
	v_basic_address
TO GROUP "gm-doctors";


-- ===================================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmDemographics-GIS-views.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-GIS-views.sql,v $', '$Revision: 1.14 $');

-- ===================================================================
-- $Log: gmDemographics-GIS-views.sql,v $
-- Revision 1.14  2004-12-20 18:52:02  ncq
-- - Ian reworked v_basic_address
--
-- Revision 1.13  2004/12/15 09:24:49  ncq
-- - addr_id -> id, followup v_basic_address changes
--
-- Revision 1.12  2004/12/15 04:18:03  ihaywood
-- minor changes
-- pointless irregularity in v_basic_address
-- extended v_basic_person to more fields.
--
-- Revision 1.11  2004/09/19 17:13:48  ncq
-- - propagate suburb into all the right places
--
-- Revision 1.10  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.9  2004/04/10 01:48:31  ihaywood
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
