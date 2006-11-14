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
-- $Id: dem-create_address.sql,v 1.1 2006-11-14 17:32:20 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
DROP function dem.create_address(text, text, text, text, text, text);
\set ON_ERROR_STOP 1

create function dem.create_address(text, text, text, text, text, text)
	returns integer
	LANGUAGE 'plpgsql'
	AS '
DECLARE
	_number ALIAS FOR $1;
	_street ALIAS FOR $2;
	_postcode ALIAS FOR $3;
	_urb ALIAS FOR $4;
	_state_code ALIAS FOR $5;
	_country_code ALIAS FOR $6;
	
	_street_id integer;
	_address_id integer;
	
	msg text;
BEGIN
	-- create/get street
	SELECT INTO _street_id dem.create_street(_street, _postcode, _urb, _state_code, _country_code);
	-- create/get and return address
	SELECT INTO _address_id a.id from dem.address a WHERE a.number ILIKE _number and a.id_street = _street_id;
	IF FOUND THEN
		RETURN _address_id;
	END IF;
	INSERT INTO dem.address (number, id_street) VALUES ( _number, _street_id);
	RETURN currval(''dem.address_id_seq'');
END;';

comment on function dem.create_address(text, text, text, text, text, text) IS
	'This function takes as parameters the number of the address,\n
	the name of the street, the postal code of the address, the\n
	name of the urb, the code of the state and the code of the\n
	country. If the country or the state do not exist in the\n
	database, the function fails.\n
	At first, the urb, the street and the address are tried to be\n
	retrieved according to the supplied information. If the fields\n
	do not match exactly an existing row, a new urb or street is\n
	created or a new address is created and returned.';

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-create_address.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-create_address.sql,v $
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
