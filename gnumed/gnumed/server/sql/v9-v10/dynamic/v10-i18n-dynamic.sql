-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-i18n-dynamic.sql,v 1.1 2008-10-12 14:58:07 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function i18n.set_curr_lang(text) cascade;
\set ON_ERROR_STOP 1


create function i18n.set_curr_lang(text)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_lang ALIAS FOR $1;
BEGIN
	if exists(select pk from i18n.translations where lang = _lang) then
		delete from i18n.curr_lang where "user" = CURRENT_USER;
		insert into i18n.curr_lang (lang) values (_lang);
		return true;
	end if;
	raise notice ''Cannot set current language to [%]. No translations available.'', _lang;
	return false;
END;
';

comment on function i18n.set_curr_lang(text) is
	'set preferred language:
	 - for "current user"
	 - only if translations for this language are available';


-- =============================================
create or replace function i18n._(text)
	returns text
	language 'plpgsql'
	security definer
	as '
DECLARE
	_orig ALIAS FOR $1;
	trans_str text;
	my_lang text;
BEGIN
	-- get language
	select into my_lang lang from i18n.curr_lang where "user" = CURRENT_USER;
	if not found then
		return _orig;
	end if;
	-- get translation
	select into trans_str trans from i18n.translations
		where lang = my_lang and orig = _orig;
	if found then
		return trans_str;
	end if;
	return _orig;
END;
';

comment on function i18n._(text) is
	'will return either the translation into
	 i18n.curr_lang.lang for the current user
	 or the input,
	 created in public schema for easy access';

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
	-- no translation available at all ?
	if not exists(select 1 from i18n.translations where orig = _orig) then
		return _orig;
	end if;
	-- get translation
	select into trans_str trans
	from i18n.translations
	where
		lang = _lang
			and
		orig = _orig;
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
create or replace function i18n.get_curr_lang()
	returns text
	language sql
	as 'select lang from i18n.curr_lang where \"user\" = current_user'
;


create or replace function i18n.get_curr_lang(text)
	returns text
	language sql
	as 'select lang from i18n.curr_lang where \"user\" = $1'
;


-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-i18n-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-i18n-dynamic.sql,v $
-- Revision 1.1  2008-10-12 14:58:07  ncq
-- - new
--
--