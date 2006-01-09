-- ======================================================
-- GNUmed fixed string internationalisation (SQL gettext)
-- ======================================================

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmI18N.sql,v $
-- $Id: gmI18N.sql,v 1.24 2006-01-09 13:42:29 ncq Exp $
-- license: GPL
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmI18N.sql,v $', '$Revision: 1.24 $');

-- =============================================
-- $Log: gmI18N.sql,v $
-- Revision 1.24  2006-01-09 13:42:29  ncq
-- - factor out dynamic stuff
-- - move into schema "i18n" (except for _())
--
-- Revision 1.23  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.22  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.21  2005/07/04 11:42:24  ncq
-- - fix _(text, text)
--
-- Revision 1.20  2005/03/31 20:08:38  ncq
-- - add i18n_upd_tx() for safe update of translations
--
-- Revision 1.19  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.18  2005/02/03 20:28:25  ncq
-- - improved comments
-- - added _(text, text)
--
-- Revision 1.17  2005/02/01 16:52:50  ncq
-- - added force_curr_lang()
--
-- Revision 1.16  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.15  2003/12/29 15:40:42  uid66147
-- - added not null
-- - added v_missing_translations
--
-- Revision 1.14  2003/06/10 09:58:11  ncq
-- - i18n() inserts strings into i18n_keys, not _(), fix comment to that effect
--
-- Revision 1.13  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.12  2003/05/02 15:06:44  ncq
-- - fix comment
--
-- Revision 1.11  2003/04/23 08:36:00  michaelb
-- made i18n_curr_lang longer still (11 to 15)
--
-- Revision 1.9  2003/02/04 13:22:01  ncq
-- - refined set_curr_lang to only work if translations available
-- - also auto-set for both "user" and "_user"
--
-- Revision 1.8  2003/02/04 12:22:52  ncq
-- - valid until in create user cannot do a sub-query :-(
-- - columns "owner" should really be of type "name" if defaulting to "CURRENT_USER"
-- - new functions set_curr_lang(*)
--
-- Revision 1.7  2003/01/24 14:16:18  ncq
-- - don't drop functions repeatedly since that will kill views created earlier
--
-- Revision 1.6  2003/01/20 20:21:53  ncq
-- - keep the last useful bit from i18n.sql as documentation
--
-- Revision 1.5  2003/01/20 19:42:47  ncq
-- - simplified creation of translating view a lot
--
-- Revision 1.4  2003/01/17 00:24:33  ncq
-- - add a few access right definitions
--
-- Revision 1.3  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.2  2003/01/04 10:30:26  ncq
-- - better documentation
-- - insert default english "translation" into i18n_translations
--
-- Revision 1.1  2003/01/01 17:41:57  ncq
-- - improved database i18n
--
