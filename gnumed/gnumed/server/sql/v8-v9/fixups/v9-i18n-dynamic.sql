-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v9-i18n-dynamic.sql,v 1.1.2.2 2008-10-22 22:02:02 ncq Exp $
-- $Revision: 1.1.2.2 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function i18n.set_curr_lang(text, name) cascade;
\set ON_ERROR_STOP 1

create or replace function i18n.set_curr_lang(text, name)
	returns boolean
	language 'plpgsql'
	security definer
	as E'
DECLARE
	_lang ALIAS FOR $1;
	_user ALIAS FOR $2;
	lang_has_tx boolean;
BEGIN
	select into lang_has_tx exists(select pk from i18n.translations where lang = _lang);

	if lang_has_tx is False then
		raise notice ''Cannot set current language to [%]. No translations available.'', _lang;
		return False;
	end if;

	delete from i18n.curr_lang where quote_ident(user) = _user;
	insert into i18n.curr_lang ("user", lang) values (_user, _lang);
	return true;
END;
';

comment on function i18n.set_curr_lang(text, name) is
	'set language to first argument for the user named in
	 the second argument if translations are available';


-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function i18n.set_curr_lang(text) cascade;
\set ON_ERROR_STOP 1

create function i18n.set_curr_lang(text)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_lang ALIAS FOR $1;
	_status boolean;
BEGIN
	select into _status i18n.set_curr_lang(_lang, CURRENT_USER);
	return _status;
END;
';

comment on function i18n.set_curr_lang(text) is
	'set preferred language:
	 - for "current user"
	 - only if translations for this language are available';

-- =============================================
create or replace function i18n.get_curr_lang(text)
	returns text
	language sql
	as 'select lang from i18n.curr_lang where "user" = $1'
;


create or replace function i18n.get_curr_lang()
	returns text
	language sql
	as 'select i18n.get_curr_lang(quote_literal(CURRENT_USER))'
;

-- =============================================
create or replace function i18n._(text, text)
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
		return _orig;
	end if;

	return trans_str;
END;
';

comment on function i18n._(text, text) is
	'will return either the translation into <text>
	 (2nd argument) for the current user or the input,
	 created in public schema for easy access';

-- =============================================
create or replace function i18n._(text)
	returns text
	language sql
	as 'select i18n._($1, i18n.get_curr_lang())';

comment on function i18n._(text) is
	'will return either the translation into
	 i18n.curr_lang.lang for the current user
	 or the input,
	 created in public schema for easy access';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-i18n-dynamic.sql,v $', '$Revision: 1.1.2.2 $');

-- ==============================================================
-- $Log: v9-i18n-dynamic.sql,v $
-- Revision 1.1.2.2  2008-10-22 22:02:02  ncq
-- - properly fix the i18n handling
--
-- Revision 1.1.2.1  2008/10/12 17:00:12  ncq
-- - be careful with "user"
--
--