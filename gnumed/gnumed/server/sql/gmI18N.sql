-- ======================================================
-- GNUmed fixed string internationalisation (SQL gettext)
-- ======================================================

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmI18N.sql,v $
-- $Id: gmI18N.sql,v 1.25 2006-02-10 14:06:40 ncq Exp $
-- license: GPL v2 or later
-- author: Karsten.Hilbert@gmx.net
-- =============================================
-- Import this script into any GNUmed database you create.

-- This will allow for transparent translation of 'fixed'
-- strings in the database. Simply switching the language in
-- i18n_curr_lang will enable the user to see another language.

-- For details please see the Developer's Guide.
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
create schema i18n authorization "gm-dbo";

-- =============================================
create table i18n.curr_lang (
	pk serial
		primary key,
	"user" name
		default CURRENT_USER
		unique
		not null,
	lang text
		not null
);

-- =============================================
create table i18n.keys (
	pk serial
		primary key,
	orig text
		unique
		not null
);

-- =============================================
create table i18n.translations (
	pk serial
		primary key,
	lang text
		not null,
	orig text
		not null,
	trans text
		not null,
	unique (lang, orig)
);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmI18N.sql,v $', '$Revision: 1.25 $');
