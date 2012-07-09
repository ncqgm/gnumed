-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;
-- --------------------------------------------------------------
\unset ON_ERROR_STOP
DROP function dem.create_urb(text, text, text, text);
\set ON_ERROR_STOP 1


CREATE function dem.create_urb(text, text, text, text)
	RETURNS integer
	AS '
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
		msg := ''combination of state + country not registered [''
			||   ''country:'' || coalesce(_country_code, ''NULL'')
			||   '', state:'' || coalesce(_state_code, ''NULL'')
			||     '', urb:'' || coalesce(_urb, ''NULL'')
			|| '', urb_zip:'' || coalesce(_urb_postcode, ''NULL'')
			|| '']'';
		RAISE EXCEPTION ''=> %'', msg;
 	END IF;
	-- get/create and return urb
	SELECT INTO _urb_id u.id from dem.urb u WHERE u.name ILIKE _urb AND u.id_state = _state_id;
	IF FOUND THEN
		RETURN _urb_id;
	END IF;
	INSERT INTO dem.urb (name, postcode, id_state) VALUES (_urb, _urb_postcode, _state_id);
	RETURN currval(''dem.urb_id_seq'');
END;' LANGUAGE 'plpgsql';


COMMENT ON function dem.create_urb(text, text, text, text) IS
	'This function takes a parameters the name of the urb,\n
	the postcode of the urb, the name of the state and the\n
	name of the country.\n
	If the country or the state does not exists in the tables,\n
	the function fails.\n
	At first, the urb is tried to be retrieved according to the\n
	supplied information. If the fields do not match exactly an\n
	existing row, a new urb is created and returned.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-dem-create_urb.sql', '18.0');
