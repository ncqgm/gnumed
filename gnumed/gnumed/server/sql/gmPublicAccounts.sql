-- GnuMed PUBLIC database accounts

-- use for publicly accessible GnuMed databases

-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- !! NEVER EVER use those accounts/passwords in a  !!
-- !! production database. As they are in CVS know- !!
-- !! ledge about them is PUBLIC and thus extremely !!
-- !! insecure. DO NOT USE FOR PRODUCTION.          !!
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmPublicAccounts.sql,v $
-- $Id: gmPublicAccounts.sql,v 1.1 2003-04-01 13:03:55 ncq Exp $
-- GPL
-- author: Karsten.Hilbert@gmx.net
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\unset ON_ERROR_STOP

-- Someone know a way of telling VALID UNTIL that the
-- value is CURRENT_DATE + interval '4 months' ?

-- ===================================================
CREATE USER "any-doc"
	WITH PASSWORD 'any-doc'
	IN GROUP "gm-doctors", "gm-public"
;
CREATE USER "_any-doc"
	WITH PASSWORD 'any-doc'
	IN GROUP "gm-doctors", "_gm-doctors", "gm-public"
;

-- ===================================================
-- do simple schema revision tracking
--\i gmSchemaRevision.sql
--\unset ON_ERROR_STOP
--INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmPublicAccounts.sql,v $', '$Revision: 1.1 $');

\set ON_ERROR_STOP 1

-- ===================================================
-- $Log: gmPublicAccounts.sql,v $
-- Revision 1.1  2003-04-01 13:03:55  ncq
-- - for public databases
--
-- Revision 1.5  2003/02/07 14:33:21  ncq
-- - can't use schema tracking since at server level we aren't guarantueed to have that
--
-- Revision 1.4  2003/02/04 12:22:53  ncq
-- - valid until in create user cannot do a sub-query :-(
-- - columns "owner" should really be of type "name" if defaulting to "CURRENT_USER"
-- - new functions set_curr_lang(*)
--
-- Revision 1.3  2003/01/30 09:02:13  ncq
-- - don't fail on failure to insert into schema revision table
--
-- Revision 1.2  2003/01/20 12:11:46  ncq
-- - typo
--
-- Revision 1.1  2003/01/19 15:30:32  ncq
-- - a few test users
--
