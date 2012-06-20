-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v11-i18n-tx_or_null.sql,v 1.1 2009-06-04 17:48:10 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
\set check_function_bodies 1
--set default_transaction_read_only to off;

-- =============================================
create or replace function i18n.tx_or_null(text, text)
	returns text
	language 'plpgsql'
	security definer
	as '
DECLARE
	_orig alias for $1;
	_lang alias for $2;
	trans_str text;
BEGIN
	select into trans_str trans from i18n.translations where lang = _lang and orig = _orig;

	if not found then
		return null;
	end if;

	return trans_str;
END;
';

comment on function i18n.tx_or_null(text, text) is
'will return either the translation into language <text> (2nd argument) or null';

-- =============================================
create or replace function i18n.tx_or_null(text)
	returns text
	language sql
	as 'select i18n.tx_or_null($1, i18n.get_curr_lang())';

comment on function i18n.tx_or_null(text) is
'will return either the translation into i18n.curr_lang.lang for the current user or null';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-i18n-tx_or_null.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-i18n-tx_or_null.sql,v $
-- Revision 1.1  2009-06-04 17:48:10  ncq
-- - first version
--
--