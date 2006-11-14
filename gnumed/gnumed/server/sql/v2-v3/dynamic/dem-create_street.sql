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
-- $Id: dem-create_street.sql,v 1.1 2006-11-14 17:32:20 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
DROP function dem.create_street(text, text, text, text, text);
\set ON_ERROR_STOP 1

CREATE function dem.create_street(text, text, text, text, text)
	RETURNS integer
	LANGUAGE 'plpgsql'
	AS '
DECLARE
	_street ALIAS FOR $1;
	_postcode ALIAS FOR $2;
	_urb ALIAS FOR $3;
	_state_code ALIAS FOR $4;
	_country_code ALIAS FOR $5;

	_urb_id integer;
	_street_id integer;

	msg text;
BEGIN
	-- create/get urb
	SELECT INTO _urb_id dem.create_urb(_urb, _postcode, _state_code, _country_code);
	-- create/get and return street
	SELECT INTO _street_id s.id from dem.street s WHERE s.name ILIKE _street AND s.id_urb = _urb_id AND postcode ILIKE _postcode;
	IF FOUND THEN
		RETURN _street_id;
	END IF;
	INSERT INTO dem.street (name, postcode, id_urb) VALUES (_street, _postcode, _urb_id);
	RETURN currval(''dem.street_id_seq'');
END;';

COMMENT ON function dem.create_street(text, text, text, text, text) IS
	'This function takes a parameters the name of the street,\n
	the postal code, the name of the urb,\n
	the postcode of the urb, the code of the state and the\n
	code of the country.\n
	If the country or the state does not exists in the tables,\n
	the function fails.\n
	At first, both the urb and street are tried to be retrieved according to the\n
	supplied information. If the fields do not match exactly an\n
	existing row, a new urb is created or a new street is created and returned.';

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-create_street.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-create_street.sql,v $
-- Revision 1.1  2006-11-14 17:32:20  ncq
-- - improve var names so we knows it's state/country *code*
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
