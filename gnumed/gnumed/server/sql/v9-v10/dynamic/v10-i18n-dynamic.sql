-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-i18n-dynamic.sql,v 1.4 2008-12-25 16:59:33 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
comment on column i18n.curr_lang.db_user is
'The database account this language setting applies to.';


\unset ON_ERROR_STOP
drop function gm.user_exists(name) cascade;
\set ON_ERROR_STOP 1


create or replace function gm.user_exists(name)
	returns boolean
	language 'plpgsql'
	as E'
BEGIN
	perform 1 from pg_user where usename = $1;

	if not FOUND then
		raise notice ''Cannot set database language. User % does not exist.'', $1;
		return false;
	end if;

	return true;
END;';


delete from i18n.curr_lang where db_user not in (
	select usename from pg_user
);


alter table i18n.curr_lang
	add constraint user_must_exist
		check (gm.user_exists(db_user) is true);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function i18n.unset_curr_lang(name) cascade;
\set ON_ERROR_STOP 1

create or replace function i18n.unset_curr_lang(name)
	returns void
	language 'plpgsql'
	security definer
	as E'
BEGIN
	delete from i18n.curr_lang where db_user = $1;
	return;
END;';

comment on function i18n.unset_curr_lang() is 'unset the db language for a user (thereby reverting to the default English)';

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function i18n.unset_curr_lang() cascade;
\set ON_ERROR_STOP 1

create or replace function i18n.unset_curr_lang()
	returns void
	language sql
	as 'select i18n.unset_curr_lang(CURRENT_USER);';

comment on function i18n.unset_curr_lang() is 'unset the db language for the current user';

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
	_db_user ALIAS FOR $2;
	lang_has_tx boolean;
BEGIN
	select into lang_has_tx exists(select pk from i18n.translations where lang = _lang);

	if lang_has_tx is False then
		raise notice ''Cannot set current language to [%]. No translations available.'', _lang;
		return False;
	end if;

	delete from i18n.curr_lang where db_user = _db_user;
	insert into i18n.curr_lang (db_user, lang) values (_db_user, _lang);
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
	as 'select lang from i18n.curr_lang where db_user = $1'
;


create or replace function i18n.get_curr_lang()
	returns text
	language sql
	as 'select i18n.get_curr_lang(CURRENT_USER)'
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
select gm.log_script_insertion('$RCSfile: v10-i18n-dynamic.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: v10-i18n-dynamic.sql,v $
-- Revision 1.4  2008-12-25 16:59:33  ncq
-- - user exists check in curr_lang
-- - unset_curr_lang
--
-- Revision 1.3  2008/10/26 01:24:21  ncq
-- - adjust for "user" -> db_user
--
-- Revision 1.2  2008/10/25 20:50:32  ncq
-- - forward port "user" fixes for v9 -> v10, too, since someone might upgrade an unpatched v9
--
-- Revision 1.1  2008/10/12 14:58:07  ncq
-- - new
--
--