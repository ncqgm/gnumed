-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-gm-nullify_empty_string.sql,v 1.1 2009-08-28 12:48:12 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

set check_function_bodies to 1;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace function gm.nullify_empty_string(text)
	returns text
	language sql
	as 'select nullif(trim($1), '''');';


grant execute on function gm.nullify_empty_string(text) to group "gm-public";

-- --------------------------------------------------------------
--create or replace function gm.trf_nullify_empty_string()
--	returns trigger
--	language 'plpgsql'
--	as '
--DECLARE
--	_col_name name;
--BEGIN
--	_col_name := TG_ARGV[0];
--
--	if NEW._col_name is null then
--		return NEW;
--	end if;
--
--	if trim(NEW._col_name) = '''' then
--		NEW._col_name := null;
--	end if;
--
--	return NEW;
--END;';
--
--
--grant execute on function gm.trf_nullify_empty_string() to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-gm-nullify_empty_string.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-gm-nullify_empty_string.sql,v $
-- Revision 1.1  2009-08-28 12:48:12  ncq
-- - add gm.nullify_empty_string()
--
--