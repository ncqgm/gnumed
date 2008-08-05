-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v8-i18n-upd_tx.sql,v 1.1.2.1 2008-08-05 18:27:14 ncq Exp $
-- $Revision: 1.1.2.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

set check_function_bodies to "on";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function i18n.upd_tx(text, text, text) cascade;
\set ON_ERROR_STOP 1


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

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v8-i18n-upd_tx.sql,v $', '$Revision: 1.1.2.1 $');

-- ==============================================================
-- $Log: v8-i18n-upd_tx.sql,v $
-- Revision 1.1.2.1  2008-08-05 18:27:14  ncq
-- - fail gracefully when lang is null
--
--
