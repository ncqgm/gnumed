-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
set default_transaction_read_only to off;
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
CREATE OR REPLACE FUNCTION i18n._(text, text)
	RETURNS text
	LANGUAGE sql
	STABLE
	AS '
SELECT COALESCE (
	(SELECT trans FROM i18n.translations WHERE lang = $2 AND orig = $1),
	-- reduce xx_XX@YY to xx
	(SELECT trans FROM i18n.translations WHERE lang = regexp_replace($2, ''_.*$'', '''') AND orig = $1),
	-- return untranslated string
	$1
)';

comment on function i18n._(text, text) is
'Returns either the translation of 1st argument into language
in 2nd argument, or the input if no translation is found.
.
Falls back to "xx" if language "xx_XX@YY" does not translate.
';

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-i18n-fixup.sql', '22.35');
