-- GnuMed database internationalisation support
-- ============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/i18n.sql,v $
-- $Revision: 1.2 $

-- license: GPL
-- author: Ian Haywood
-- Copyright (C) 2002 Ian Haywood

-- This script should be run on all databases that need i18n before the main script.
-- the main script should start by filling i18n_strings and i18n_trans with its own
-- strings.

-- WARNING: PL/SQL must be working!
-- ============================================
\unset ON_ERROR_STOP

create table i18n_active_lang (
	code varchar (5)
);

comment on table lang is
	'this table contains ONLY EVER ONE ROW, containing the current language code';

-- ============================================
create function set_lang (text) returns unknown as '
	delete from lang;
	insert into lang (code) values ($1);
	select NULL;
' language 'sql';

-- ============================================
create table i18n_strings (
	id serial,
	str text unique
);

comment on table i18n_strings is
	'table of translatable strings, automatically filled by _(text)';

-- ============================================
create table i18n_trans (
	id_str integer references i18n_strings (id),
	trans_str text,
	code varchar (5)
);

comment on table i18n_trans is
	'table of translations, must be filled by translators.';

-- ============================================
create function _ (text) returns text as '
DECLARE
	lang_code varchar (5);
	reply text;
BEGIN
	select into lang_code code from lang;
	select into reply trans_str
		from
			i18n_trans, i18n_strings
		where
			i18n_strings.id = id_str
				and
			i18n_trans.code = lang_code
				and
			i18n_strings.str = $1;
	if not found then
		reply := $1;
		if not exists (select * from i18n_strings where str = $1) then 
			insert into i18n_strings (str) values ($1); 
		end if;
	end if;
	return reply;
END;
' language 'plpgsql';

comment on function _ (text) is
	'called in the ER scripts for all strings inserted into the database that require translation.
	 _(text) will look up the string in i18n_trans and return the translation. If not found, the 
	 string is inserted into i18n_strings.';

\set ON_ERROR_STOP 1
