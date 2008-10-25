-- ======================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/v8-v9/dynamic/v9-i18n-dynamic.sql,v $
-- $Id: v9-i18n-dynamic.sql,v 1.4 2008-10-25 20:47:16 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

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


create or replace function i18n._(text)
	returns text
	language sql
	as 'select i18n._($1, i18n.get_curr_lang())';

comment on function i18n._(text) is
	'will return either the translation into
	 i18n.curr_lang.lang for the current user
	 or the input,
	 created in public schema for easy access';


-- =============================================
create or replace function public._(text)
	returns text
	language sql
	as 'select i18n._($1)';


create or replace function public._(text, text)
	returns text
	language sql
	as 'select i18n._($1, $2)';


-- =============================================
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
create or replace function i18n.upd_tx(text, text, text)
	returns boolean
	language 'plpgsql'
	security definer
	as '
declare
	_lang alias for $1;
	_orig alias for $2;
	_trans alias for $3;
	_tmp text;
begin
	if _lang is null then
		raise notice ''i18n.upd_tx(text, text, text): Cannot create translation for language <NULL>.'';
		return False;
	end if;

	if _trans = _orig then
		raise notice ''i18n.upd_tx(text, text, text): Original = translation. Skipping.'';
		return True;
	end if;

	select into _tmp ''1'' from i18n.keys where orig = _orig;
	if not found then
		raise notice ''i18n.upd_tx(text, text, text): [%] not found in i18n.keys. Creating entry.'', _orig;
		insert into i18n.keys (orig) values (_orig);
	end if;

	delete from i18n.translations where lang = _lang and orig = _orig;
	insert into i18n.translations (lang, orig, trans) values (_lang, _orig, _trans);

	raise notice ''i18n.upd_tx(%: [%] ==> [%])'', _lang, _orig, _trans;
	return True;
end;'
;


create or replace function i18n.upd_tx(text, text)
	returns boolean
	language sql
	security definer
	as 'select i18n.upd_tx((select i18n.get_curr_lang()), $1, $2)'
;

-- =============================================
select gm.log_script_insertion('$RCSfile: v9-i18n-dynamic.sql,v $', '$Revision: 1.4 $');

-- =============================================
-- $Log: v9-i18n-dynamic.sql,v $
-- Revision 1.4  2008-10-25 20:47:16  ncq
-- - port "user" fixes from 0.3 branch
--
-- Revision 1.3  2008/08/03 20:04:26  ncq
-- - gracefully fail on lang == null
--
-- Revision 1.2  2008/07/24 14:03:58  ncq
-- - get_curr_lang
-- - improved upd_tx(text, text, text)
-- - upd_tx(text, text)
--
-- Revision 1.1  2008/03/25 19:34:21  ncq
-- - make public._() a wrapper around the real i18n._()
--
--