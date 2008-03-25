-- ======================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/v8-v9/dynamic/v9-i18n-dynamic.sql,v $
-- $Id: v9-i18n-dynamic.sql,v 1.1 2008-03-25 19:34:21 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

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
create or replace function public._(text)
	returns text
	language sql
	as 'select i18n._($1)';


create or replace function public._(text, text)
	returns text
	language sql
	as 'select i18n._($1, $2)';

-- =============================================
select gm.log_script_insertion('$RCSfile: v9-i18n-dynamic.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: v9-i18n-dynamic.sql,v $
-- Revision 1.1  2008-03-25 19:34:21  ncq
-- - make public._() a wrapper around the real i18n._()
--
--