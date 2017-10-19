-- ======================================================
-- GNUmed fixed string internationalisation (SQL gettext)
-- ======================================================

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmI18N-dynamic.sql,v $
-- $Id: gmI18N-dynamic.sql,v 1.5 2006-07-24 14:18:52 ncq Exp $
-- license: GPL v2 or later
-- author: Karsten.Hilbert@gmx.net
-- =============================================
-- Import this script into any GNUmed database you create.

-- This will allow for transparent translation of 'fixed'
-- strings in the database. Simply switching the language in
-- i18n_curr_lang will enable the user to see another language.

-- For details please see the Developer's Guide.
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
comment on table i18n.curr_lang is
	'holds the currently selected per-user default
	 language for fixed strings in the database';

-- =============================================
comment on table i18n.keys is
	'this table holds all the original strings that need
	 translation so give this to your language teams,
	 the function i18n.i18n() will take care to enter relevant
	 strings into this table, the table table does NOT
	 play any role in runtime translation activity';

-- =============================================
\unset ON_ERROR_STOP
drop index i18n.idx_orig;
\set ON_ERROR_STOP 1

create index idx_orig on i18n.translations(orig);

comment on table i18n.translations is
	'this table holds all the translated strings';
comment on column i18n.translations.lang is
	'the language (corresponding to i18n.curr_lang for
	 a given user) that this translation belongs to';
comment on column i18n.translations.orig is
	'the original, untranslated string, used as the search key.';
comment on column i18n.translations.trans is
	'the translation of <orig> into <lang>';

-- =============================================
create or replace function i18n.i18n(text)
	returns text
	language 'plpgsql'
	security definer
	as '
DECLARE
	original ALIAS FOR $1;
BEGIN
	if not exists(select pk from i18n.keys where orig = original) then
		insert into i18n.keys (orig) values (original);
	end if;
	return original;
END;
';

comment on function i18n.i18n(text) is
	'insert original strings into i18n.keys for later translation';

-- =============================================
-- FIXME: if _orig does not exist - call i18n() on it ?
-- FIXME: support upd_tx(text, text) and take language from curr_lang
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
	select into _tmp ''1'' from i18n.keys where orig=_orig;
	if not found then
		_tmp := ''String "'' || _orig || ''" not found in i18n.keys. No use storing translation.'';
		raise notice ''%'', _tmp;
		-- return ''String "'' || _orig || ''" not found in i18n.keys. No use storing translation.'';
		return False;
	end if;
	delete from i18n.translations where lang=_lang and orig=_orig;
	insert into i18n.translations (lang, orig, trans) values (_lang, _orig, _trans);
	-- return _orig || '' == ('' || _lang || '') ==> '' || _trans;
	return True;
end;';

-- =============================================
create or replace function _(text)
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
	select into my_lang lang from i18n.curr_lang where user = CURRENT_USER;
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

comment on function _(text) is
	'will return either the translation into
	 i18n.curr_lang.lang for the current user
	 or the input,
	 created in public schema for easy access';

-- =============================================
create or replace function _(text, text)
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

comment on function _(text, text) is
	'will return either the translation into <text>
	 (2nd argument) for the current user or the input,
	 created in public schema for easy access';

-- =============================================
create or replace function i18n.set_curr_lang(text)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_lang ALIAS FOR $1;
BEGIN
	if exists(select pk from i18n.translations where lang = _lang) then
		delete from i18n.curr_lang where user = CURRENT_USER;
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
create or replace function i18n.force_curr_lang(text)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
    _lang ALIAS FOR $1;
BEGIN
    raise notice ''Forcing current language to [%] without checking for translations..'', _lang;
    delete from i18n.curr_lang where user = CURRENT_USER;
    insert into i18n.curr_lang(lang) values (_lang);
    return 1;
END;
';

comment on function i18n.force_curr_lang(text) is
	'force preferred language to some language:
	 - for "current user"';

-- =============================================
create or replace function i18n.set_curr_lang(text, name)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_lang ALIAS FOR $1;
	_user ALIAS FOR $2;
BEGIN
	if exists(select pk from i18n.translations where lang = _lang) then
		delete from i18n.curr_lang where user = _user;
		insert into i18n.curr_lang("user", lang) values (_user, _lang);
		return true;
	end if;
	raise notice ''Cannot set current language to [%]. No translations available.'', _lang;
	return False;
END;
';

comment on function i18n.set_curr_lang(text, name) is
	'set language to first argument for the user named in
	 the second argument if translations are available';

-- =============================================
\unset ON_ERROR_STOP
drop view i18n.v_missing_translations;
\set ON_ERROR_STOP 1

create view i18n.v_missing_translations as
select
	icl.lang,
	ik.orig
from
	(select distinct on (lang) lang from i18n.curr_lang) as icl,
	i18n.keys ik
where
	ik.orig not in (select orig from i18n.translations)
;

comment on view i18n.v_missing_translations is
	'lists per language which strings are lacking a translation';

-- =============================================
grant usage on schema i18n to group "gm-public";

GRANT SELECT on
	i18n.curr_lang
	, i18n.keys
	, i18n.translations
	, i18n.v_missing_translations
TO group "gm-public";

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmI18N-dynamic.sql,v $', '$Revision: 1.5 $');
