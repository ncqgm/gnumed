-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-create_urb.sql,v 1.1 2006-11-19 10:13:32 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
DROP function dem.create_urb(text, text, text, text);
\set ON_ERROR_STOP 1

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
select public.log_script_insertion('$RCSfile: dem-create_urb.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-create_urb.sql,v $
-- Revision 1.1  2006-11-19 10:13:32  ncq
-- - use coalesce on raise exception
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
