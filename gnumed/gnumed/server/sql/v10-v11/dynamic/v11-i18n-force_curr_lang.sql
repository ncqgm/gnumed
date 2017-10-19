-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v11-i18n-force_curr_lang.sql,v 1.3 2009-07-21 13:15:26 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
\set check_function_bodies 1
--set default_transaction_read_only to off;

-- =============================================
\unset ON_ERROR_STOP
drop function i18n.force_curr_lang(text, name) cascade;
\set ON_ERROR_STOP 1


create or replace function i18n.force_curr_lang(text, name)
	returns boolean
	language 'plpgsql'
	security definer
	as E'
DECLARE
	_lang ALIAS FOR $1;
	_db_user ALIAS FOR $2;
BEGIN
    raise notice ''Forcing current language for [%] to [%] without checking for translations...'', _db_user, _lang;
    delete from i18n.curr_lang where db_user = _db_user;
    insert into i18n.curr_lang(db_user, lang) values (_db_user, _lang);
    return True;
END;
';


comment on function i18n.force_curr_lang(text, name) is
'force preferred language to some language for a user';

-- =============================================
create or replace function i18n.force_curr_lang(text)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
    _lang ALIAS FOR $1;
	_status boolean;
BEGIN
	select into _status i18n.force_curr_lang(_lang, CURRENT_USER);
	return _status;
END;';


comment on function i18n.force_curr_lang(text) is
'force preferred language to some language for "current user"';

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
select gm.log_script_insertion('$RCSfile: v11-i18n-force_curr_lang.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v11-i18n-force_curr_lang.sql,v $
-- Revision 1.3  2009-07-21 13:15:26  ncq
-- - fix faulty table INSERT
--
-- Revision 1.2  2009/07/21 13:08:34  ncq
-- - fix faulty column access
--
-- Revision 1.1  2009/07/09 16:09:28  ncq
-- - force_curr_lang always set the user to gm-dbo rather than the intended one
--
--
