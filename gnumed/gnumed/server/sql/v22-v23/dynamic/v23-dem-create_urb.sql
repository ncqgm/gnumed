-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
DROP function if exists dem.create_urb(text, text, text, text);


CREATE function dem.create_urb(text, text, text, text)
	RETURNS integer
	AS '
DECLARE
	_urb ALIAS FOR $1;
	_urb_postcode ALIAS FOR $2;
	_region_code ALIAS FOR $3;
	_country_code ALIAS FOR $4;

 	_region_pk integer;
	_urb_id integer;

	msg text;
BEGIN
 	-- get region
 	SELECT INTO _region_pk d_r.pk from dem.region d_r WHERE d_r.code = _region_code and d_r.country = _country_code;
 	IF NOT FOUND THEN
		msg := ''combination of region + country not registered [''
			||   ''country:'' || coalesce(_country_code, ''NULL'')
			||  '', region:'' || coalesce(_region_code, ''NULL'')
			||     '', urb:'' || coalesce(_urb, ''NULL'')
			|| '', urb_zip:'' || coalesce(_urb_postcode, ''NULL'')
			|| '']'';
		RAISE EXCEPTION ''=> %'', msg;
 	END IF;
	-- get/create and return urb
	SELECT INTO _urb_id u.id from dem.urb u WHERE u.name ILIKE _urb AND u.fk_region = _region_pk AND u.postcode ILIKE _urb_postcode;
	IF FOUND THEN
		RETURN _urb_id;
	END IF;
	INSERT INTO dem.urb (name, postcode, fk_region) VALUES (_urb, _urb_postcode, _region_pk);
	RETURN currval(''dem.urb_id_seq'');
END;' LANGUAGE 'plpgsql';


COMMENT ON function dem.create_urb(text, text, text, text) IS
	'This function takes as parameters the name of the urb,\n
	the postcode of the urb, the name of the region and the\n
	name of the country.\n
	If the country or the region does not exists in the tables,\n
	the function fails.\n
	At first, the urb is tried to be retrieved according to the\n
	supplied information. If the fields do not match exactly an\n
	existing row, a new urb is created and returned.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-create_urb.sql', '23.0');
