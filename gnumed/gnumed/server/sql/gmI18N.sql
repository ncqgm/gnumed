-- =============================================
-- GnuMed fixed string internationalisation
-- ========================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmI18N.sql,v $
-- $Id: gmI18N.sql,v 1.21 2005-07-04 11:42:24 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net
-- =============================================
-- Import this script into any GnuMed database you create.

-- This will allow for transparent translation of 'fixed'
-- strings in the database. Simply switching the language in
-- i18n_curr_lang will enable the user to see another language.

-- For details please see the Developer's Guide.
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
create table i18n_curr_lang (
	id serial primary key,
	owner name default CURRENT_USER unique not null,
	lang text not null
);

comment on table i18n_curr_lang is
	'holds the currently selected per-user default
	 language for fixed strings in the database';

-- =============================================
create table i18n_keys (
	id serial primary key,
	orig text unique not null
);

comment on table i18n_keys is
	'this table holds all the original strings that need
	 translation so give this to your language teams,
	 the function i18n() will take care to enter relevant
	 strings into this table, the table table does NOT
	 play any role in runtime translation activity';

-- =============================================
create table i18n_translations (
	id serial primary key,
	lang text not null,
	orig text not null,
	trans text not null,
	unique (lang, orig)
);
create index idx_orig on i18n_translations(orig);

comment on table i18n_translations is
	'this table holds all the translated strings';
comment on column i18n_translations.lang is
	'the language (corresponding to i18n_curr_lang for
	 a given user) that this translation belongs to';
comment on column i18n_translations.orig is
	'the original, untranslated string, used as the search key.';
comment on column i18n_translations.trans is
	'the translation of <orig> into <lang>';

-- =============================================
create function i18n(text) returns text as '
DECLARE
	original ALIAS FOR $1;
BEGIN
	if not exists(select id from i18n_keys where orig = original) then
		insert into i18n_keys (orig) values (original);
	end if;
	return original;
END;
' language 'plpgsql';

comment on function i18n(text) is
	'insert original strings into i18n_keys for later translation';

-- =============================================
create function i18n_upd_tx(text, text, text) returns boolean as '
declare
	_lang alias for $1;
	_orig alias for $2;
	_trans alias for $3;
	_tmp text;
begin
	select into _tmp ''1'' from i18n_keys where orig=_orig;
	if not found then
		_tmp := ''String "'' || _orig || ''" not found in i18n_keys. No use storing translation.'';
		raise notice ''%'', _tmp;
		-- return ''String "'' || _orig || ''" not found in i18n_keys. No use storing translation.'';
		return False;
	end if;
	delete from i18n_translations where lang=_lang and orig=_orig;
	insert into i18n_translations (lang, orig, trans) values (_lang, _orig, _trans);
	-- return _orig || '' == ('' || _lang || '') ==> '' || _trans;
	return True;
end;' language 'plpgsql';

-- =============================================
create function _(text) returns text as '
DECLARE
    orig_str ALIAS FOR $1;
    trans_str text;
    my_lang text;
BEGIN
    -- get language
    select into my_lang lang
	from i18n_curr_lang
    where
	owner = CURRENT_USER;
    if not found then
	return orig_str;
    end if;
    -- get translation
    select into trans_str trans
	from i18n_translations
    where
	lang = my_lang
	    and
	orig = orig_str;
    if not found then
	return orig_str;
    end if;
    return trans_str;
END;
' language 'plpgsql';

comment on function _(text) is
	'will return either the translation into i18n_curr_lang.lang
	 for the current user or the input';

-- =============================================
create function _(text, text) returns text as '
DECLARE
	_orig alias for $1;
	_lang alias for $2;
	trans_str text;
BEGIN
	-- no translation available at all ?
	if not exists(select 1 from i18n_translations where orig = _orig) then
		return _orig;
	end if;
	-- get translation
	select into trans_str trans
	from i18n_translations
	where
		lang = _lang
			and
		orig = _orig;
	if not found then
		return _orig;
	end if;
	return trans_str;
END;
' language 'plpgsql';

comment on function _(text, text) is
	'will return either the translation into <text> (2nd
	 argument) for the current user or the input';

-- =============================================
create function set_curr_lang(text) returns unknown as '
DECLARE
	language ALIAS FOR $1;
BEGIN
	if exists(select id from i18n_translations where lang = language) then
		delete from i18n_curr_lang where owner = CURRENT_USER;
		insert into i18n_curr_lang (lang) values (language);
		return 1;
	else
		raise exception ''Cannot set current language to [%]. No translations available.'', language;
		return NULL;
	end if;
	return NULL;
END;
' language 'plpgsql';

comment on function set_curr_lang(text) is
	'set preferred language:
	 - for "current user"
	 - only if translations for this language are available';

-- =============================================
create function force_curr_lang(text) returns unknown as '
DECLARE
    language ALIAS FOR $1;
BEGIN
    raise notice ''Forcing current language to [%] without checking for translations..'', language;
    delete from i18n_curr_lang where owner = CURRENT_USER;
    insert into i18n_curr_lang (lang) values (language);
    return 1;
END;
' language 'plpgsql';

comment on function force_curr_lang(text) is
	'force preferred language to some language:
	 - for "current user"';

-- =============================================
create function set_curr_lang(text, name) returns unknown as '
DECLARE
	language ALIAS FOR $1;
	username ALIAS FOR $2;
BEGIN
	if exists(select id from i18n_translations where lang = language) then
		delete from i18n_curr_lang where owner = username;
		insert into i18n_curr_lang (owner, lang) values (username, language);
		return 1;
	else
		raise exception ''Cannot set current language to [%]. No translations available.'', language;
		return NULL;
	end if;
	return NULL;
END;
' language 'plpgsql';

comment on function set_curr_lang(text, name) is
	'set language to first argument for the user named in
	 the second argument if translations are available';

-- =============================================
\unset ON_ERROR_STOP
drop view v_missing_translations;
\set ON_ERROR_STOP 1

create view v_missing_translations as
select
	icl.lang,
	ik.orig
from
	(select distinct on (lang) lang from i18n_curr_lang) as icl,
	i18n_keys ik
where
	ik.orig not in (select orig from i18n_translations)
;

comment on view v_missing_translations is
	'lists per language which strings are missing a translation';

-- =============================================
-- there's most likely no harm in granting select to all
GRANT SELECT on
	i18n_curr_lang
	, i18n_keys
	, i18n_translations
	, v_missing_translations
TO group "gm-public";

-- users need to be able to change this
-- FIXME: more groups need to have access here
GRANT SELECT, INSERT, UPDATE, DELETE on
	i18n_curr_lang,
	i18n_curr_lang_id_seq
TO group "gm-doctors";

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmI18N.sql,v $', '$Revision: 1.21 $');

-- =============================================
-- $Log: gmI18N.sql,v $
-- Revision 1.21  2005-07-04 11:42:24  ncq
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
