-- ======================================================
-- GNUmed fixed string internationalisation (SQL gettext)
-- ======================================================

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmI18N-dynamic.sql,v $
-- $Id: gmI18N-dynamic.sql,v 1.2 2006-01-10 08:44:22 ncq Exp $
-- license: GPL
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
drop index idx_orig;
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
	returns unknown
	language 'plpgsql'
	security definer
	as '
DECLARE
	_lang ALIAS FOR $1;
BEGIN
	if exists(select pk from i18n.translations where lang = _lang) then
		delete from i18n.curr_lang where user = CURRENT_USER;
		insert into i18n.curr_lang (lang) values (_lang);
		return 1;
	else
		raise exception ''Cannot set current language to [%]. No translations available.'', _lang;
		return NULL;
	end if;
	return NULL;
END;
';

comment on function i18n.set_curr_lang(text) is
	'set preferred language:
	 - for "current user"
	 - only if translations for this language are available';

-- =============================================
create function i18n.force_curr_lang(text)
	returns unknown
	language 'plpgsql'
	security definer
	as '
DECLARE
    _lang ALIAS FOR $1;
BEGIN
    raise notice ''Forcing current language to [%] without checking for translations..'', _lang;
    delete from i18n.curr_lang where user = CURRENT_USER;
    insert into i18n.curr_lang (lang) values (_lang);
    return 1;
END;
';

comment on function i18n.force_curr_lang(text) is
	'force preferred language to some language:
	 - for "current user"';

-- =============================================
create function i18n.set_curr_lang(text, name)
	returns unknown
	language 'plpgsql'
	security definer
	as '
DECLARE
	_lang ALIAS FOR $1;
	_user ALIAS FOR $2;
BEGIN
	if exists(select pk from i18n.translations where lang = _lang) then
		delete from i18n.curr_lang where user = _user;
		insert into i18n.curr_lang (user, lang) values (_user, _lang);
		return 1;
	else
		raise exception ''Cannot set current language to [%]. No translations available.'', _lang;
		return NULL;
	end if;
	return NULL;
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmI18N-dynamic.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmI18N-dynamic.sql,v $
-- Revision 1.2  2006-01-10 08:44:22  ncq
-- - drop index does not require "on"
--
-- Revision 1.1  2006/01/09 13:42:29  ncq
-- - factor out dynamic stuff
-- - move into schema "i18n" (except for _())
--
-- Revision 1.23  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.22  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.21  2005/07/04 11:42:24  ncq
-- - fix _(text, text)
--
-- Revision 1.20  2005/03/31 20:08:38  ncq
-- - add i18n_upd_tx() for safe update of translations
--
-- Revision 1.19  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.18  2005/02/03 20:28:25  ncq
-- - improved comments
-- - added _(text, text)
--
-- Revision 1.17  2005/02/01 16:52:50  ncq
-- - added force_curr_lang()
--
-- Revision 1.16  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.15  2003/12/29 15:40:42  uid66147
-- - added not null
-- - added v_missing_translations
--
-- Revision 1.14  2003/06/10 09:58:11  ncq
-- - i18n() inserts strings into i18n_keys, not _(), fix comment to that effect
--
-- Revision 1.13  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.12  2003/05/02 15:06:44  ncq
-- - fix comment
--
-- Revision 1.11  2003/04/23 08:36:00  michaelb
-- made i18n_curr_lang longer still (11 to 15)
--
-- Revision 1.9  2003/02/04 13:22:01  ncq
-- - refined set_curr_lang to only work if translations available
-- - also auto-set for both "user" and "_user"
--
-- Revision 1.8  2003/02/04 12:22:52  ncq
-- - valid until in create user cannot do a sub-query :-(
-- - columns "owner" should really be of type "name" if defaulting to "CURRENT_USER"
-- - new functions set_curr_lang(*)
--
-- Revision 1.7  2003/01/24 14:16:18  ncq
-- - don't drop functions repeatedly since that will kill views created earlier
--
-- Revision 1.6  2003/01/20 20:21:53  ncq
-- - keep the last useful bit from i18n.sql as documentation
--
-- Revision 1.5  2003/01/20 19:42:47  ncq
-- - simplified creation of translating view a lot
--
-- Revision 1.4  2003/01/17 00:24:33  ncq
-- - add a few access right definitions
--
-- Revision 1.3  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.2  2003/01/04 10:30:26  ncq
-- - better documentation
-- - insert default english "translation" into i18n_translations
--
-- Revision 1.1  2003/01/01 17:41:57  ncq
-- - improved database i18n
--
