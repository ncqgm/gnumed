-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table i18n.translations drop constraint i18n_translations_sane_trans;
\set ON_ERROR_STOP 1

delete from i18n.translations where orig = trans;

alter table i18n.translations
	add constraint i18n_translations_sane_trans check
		(trans <> orig);

-- --------------------------------------------------------------
create or replace function i18n.untranslate(text, text)
	returns text
	language 'plpgsql'
	as '
DECLARE
	_trans alias for $1;
	_lang alias for $2;
	_orig text;
BEGIN
	select orig into _orig
	from i18n.translations
	where
		trans = _trans
			and
		lang = _lang;

	return _orig;
END;';


comment on function i18n.untranslate(text, text) is
	'Return "original" from a "translated" string (1st argument) as per language (2nd argument).';

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-i18n-translations-dynamic.sql', '17.0');
