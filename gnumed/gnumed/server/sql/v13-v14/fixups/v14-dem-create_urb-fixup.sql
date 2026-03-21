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

CREATE function dem.create_urb(text, text, text, text) RETURNS integer AS '
DECLARE
	_urb ALIAS FOR $1;
	_urb_postcode ALIAS FOR $2;	
	_state_code ALIAS FOR $3;
	_country_code ALIAS FOR $4;

 	_state_id integer;
	_urb_id integer;

	msg text;
BEGIN
 	-- get state
 	SELECT INTO _state_id s.id from dem.state s WHERE s.code = _state_code and s.country = _country_code;
 	IF NOT FOUND THEN
		msg := ''Cannot set address ['' || coalesce(_country_code, ''country_code:NULL'') || '', '' || coalesce(_state_code, ''state_code:NULL'') || '', '' || coalesce(_urb, ''urb:NULL'') || '', '' || coalesce(_urb_postcode, ''urb_postcode:NULL'') || ''].'';
		RAISE EXCEPTION ''=> %'', msg;
 	END IF;
	-- get/create and return urb
	SELECT INTO _urb_id u.id from dem.urb u WHERE u.name ILIKE _urb AND u.id_state = _state_id AND u.postcode ILIKE _urb_postcode;
	IF FOUND THEN
		RETURN _urb_id;
	END IF;
	INSERT INTO dem.urb (name, postcode, id_state) VALUES (_urb, _urb_postcode, _state_id);
	RETURN currval(''dem.urb_id_seq'');
END;' LANGUAGE 'plpgsql';

COMMENT ON function dem.create_urb(text, text, text, text) IS '
This function takes as parameters\n
- the name of the urb,\n
- the postcode of the urb,\n
- the name of the state and\n
- the name of the country.\n
\n
If country or state do not exists in the tables,\n
the function fails.\n
\n
At first, the urb is tried to be retrieved according to the\n
supplied information. If the fields do not match exactly an\n
existing row, a new urb is created and returned.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-dem-create_urb-fixup.sql', '14.6');
