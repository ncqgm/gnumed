-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-gm-nullify_empty_string.sql,v 1.2 2009-11-29 16:06:51 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

set check_function_bodies to 1;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace function gm.nullify_empty_string(text)
	returns text
	language 'plpgsql'
	as '
DECLARE
	_input alias for $1;
BEGIN
	if _input is null then
		return null;
	end if;

	if trim(_input) = '''' then
		return null;
	end if;

	return _input;
END;';


grant execute on function gm.nullify_empty_string(text) to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-gm-nullify_empty_string.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-gm-nullify_empty_string.sql,v $
-- Revision 1.2  2009-11-29 16:06:51  ncq
-- - turn into psql func, and fix wrongly returning trim()ed result in passing
--
-- Revision 1.1  2009/08/28 12:48:12  ncq
-- - add gm.nullify_empty_string()
--
--