-- ======================================================
-- GNUmed fixed string internationalisation (SQL gettext)
-- ======================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
drop function if exists i18n.set_curr_lang(text) cascade;

create function i18n.set_curr_lang(text)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
	_lang ALIAS FOR $1;
BEGIN
	if exists(select pk from i18n.translations where lang = _lang) then
		delete from i18n.curr_lang where db_user = SESSION_USER;
		insert into i18n.curr_lang (lang, db_user) values (_lang, SESSION_USER);
		return true;
	end if;
	raise notice ''Cannot set current language to [%]. No translations available.'', _lang;
	return false;
END;
';

comment on function i18n.set_curr_lang(text) is
	'set preferred language:
	 - for "current (session) user"
	 - only if translations for this language are available';

-- =============================================
drop function if exists i18n.force_curr_lang(text) cascade;

create function i18n.force_curr_lang(text)
	returns boolean
	language 'plpgsql'
	security definer
	as '
DECLARE
    _lang ALIAS FOR $1;
BEGIN
    raise notice ''Forcing current language to [%] without checking for translations..'', _lang;
    delete from i18n.curr_lang where db_user = SESSION_USER;
	insert into i18n.curr_lang (lang, db_user) values (_lang, SESSION_USER);
    return true;
END;
';

comment on function i18n.force_curr_lang(text) is
	'force preferred language to some language:
	 - for "current user"';

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-i18n-lang_funcs-fixup.sql', '22.11');
