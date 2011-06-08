-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-gm-is_null_or_non_empty_string.sql,v 1.1 2009-03-16 15:13:03 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace function gm.is_null_or_non_empty_string(text)
	returns boolean
	language sql
	as 'select (coalesce(trim($1), ''NULL'') != '''');';


grant execute on function gm.is_null_or_non_empty_string(text) to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-gm-is_null_or_non_empty_string.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-gm-is_null_or_non_empty_string.sql,v $
-- Revision 1.1  2009-03-16 15:13:03  ncq
-- - new
--
--