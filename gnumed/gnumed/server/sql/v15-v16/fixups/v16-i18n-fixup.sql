-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
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
		-- reduce xx_XX@YY to xx
		select into trans_str trans from i18n.translations where lang = regexp_replace(_lang, ''_.*$'', '''') and orig = _orig;

		if not found then
			return _orig;
		end if;

--		if not found then
--			-- check "generic" dummy translation used to work around accentuation problems
--			select into trans_str trans from i18n.translations where lang = ''generic'' and orig = _orig;
--
--			if not found then
--				return _orig;
--			end if;
--		end if;

	end if;

	return trans_str;
END;
';

comment on function i18n._(text, text) is
'will return either the translation into <lang>::text
 (2nd argument) for the current user or the input,
 created in public schema for easy access,
 will fallback to "xx" if xx_XX does not exist';

select _('brother');

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-i18n-fixup.sql', '16.6');

-- ==============================================================
