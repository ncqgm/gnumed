-- =============================================
-- GnuMed fixed string internationalisation
-- ========================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmI18N.sql,v $
-- $Id: gmI18N.sql,v 1.2 2003-01-04 10:30:26 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net
-- =============================================
-- Include this file at the top of your psql script schema definition files.
-- For your convenience, just copy/paste the following two lines:
-- do fixed string i18n()ing
--\i gmI18N.sql

-- This will allow for transparent translation of 'fixed'
-- strings in the database. Simply switching the language in
-- i18n_curr_lang will enable the user to see another language.

-- For your database tables to take advantage of this you need to
-- create views that pull translations from i18n_translations based
-- on the original (English) string as the key, eg.

-- Your table is:

--	create table relations (
--		id serial primary key,
--		name varchar(10) unique
--	);

-- You would need to create a view like:

--	create view v_i18n_relations as
--		select
--			rel.id, tr.trans as name
--		from
--			relations as rel,
--			i18n_translations as tr,
--			i18n_curr_lang as lcurr
--		where
--			lcurr.owner = CURRENT_USER::varchar
--				and
--			tr.lang = lcurr.lang
--		;

-- Now, if you want to support i18n()ed 'sisters':
--  insert into relations (name) values (_('sister'));

-- This will insert the original string into i18n_keys so translators
-- know about all the strings to translate, it will also insert the
-- original as it's own default translation into i18n_translations
-- for the language setting en_GB. Which also means that original
-- strings should be English. Sorry. (But they do not have too.)

-- Thus you also need to insert a translation for, say, German:
--  insert into i18n_translations (lang, orig, trans) values ('de_DE', 'sister', 'Schwester');

-- Of course, the clients need to be aware of this fact and
-- access the views instead of the actual tables.

-- This i18n technique does not take care of strings that are inserted
-- into the database dynamically (at runtime). It only makes sense for
-- strings that are inserted once. Such strings are often used for
-- enumerations.

-- All this crap isn't necessary anymore once PostgreSQL supports
-- native internationalization of 'fixed' strings.

-- FIXME: we need a way to return the original as a default
-- if there's no translation available
-- =============================================
\unset ON_ERROR_STOP

create table i18n_curr_lang (
	id serial primary key,
	owner varchar(20) default CURRENT_USER,
	lang varchar(10)
);

comment on table i18n_curr_lang is
	'holds the currently selected language per user for fixed strings in the database';

-- =============================================
create table i18n_keys (
	id serial primary key,
	orig text unique
);

comment on table i18n_keys is
	'this table holds all the original strings that need translation so give this to your language teams,
	the function _() will take care to enter relevant strings into this table';

-- =============================================
create table i18n_translations (
	id serial primary key,
	lang varchar(10),
	orig text,
	trans text
);
create index idx_orig on i18n_translations(orig);
-- can we have a rule/trigger here that would return the
-- original in case there's no translation available ?

-- =============================================
create function _ (text) returns text as '
DECLARE
	original ALIAS FOR $1;
BEGIN
	insert into i18n_keys (orig) values (original);
	insert into i18n_translations (lang, orig, trans) values (''en_GB'', original, original);
	return original;
END;
' language 'plpgsql';

comment on function _ (text) is
	'_(text) will insert original strings into i18n_keys for later translation,
	it will also insert a default English translation into i18n_translations';

\set ON_ERROR_STOP 1

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmI18N.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmI18N.sql,v $
-- Revision 1.2  2003-01-04 10:30:26  ncq
-- - better documentation
-- - insert default english "translation" into i18n_translations
--
-- Revision 1.1  2003/01/01 17:41:57  ncq
-- - improved database i18n
--
