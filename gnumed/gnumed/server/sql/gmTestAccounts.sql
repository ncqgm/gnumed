-- GnuMed database test accounts

-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- !! NEVER EVER use those accounts/passwords in a  !!
-- !! production database. As they are in CVS know- !!
-- !! ledge about them is PUBLIC and thus extremely !!
-- !! insecure. DO NOT USE FOR PRODUCTION.          !!
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmTestAccounts.sql,v $
-- $Id: gmTestAccounts.sql,v 1.7 2003-06-11 12:51:07 ncq Exp $
-- GPL
-- author: Karsten.Hilbert@gmx.net
-- ===================================================================
-- must ignore errors so we don't fail on
-- accounts that exist already
\unset ON_ERROR_STOP

-- Anyone know a way of telling VALID UNTIL that the
-- value is CURRENT_DATE + interval '4 months' ?

-- ===================================================
CREATE USER "test-doc"
	WITH PASSWORD 'test-doc'
	IN GROUP "gm-doctors", "gm-public"
	VALID UNTIL '2003-09-30'
;
CREATE USER "_test-doc"
	WITH PASSWORD 'test-doc'
	IN GROUP "gm-doctors", "_gm-doctors", "gm-public"
	VALID UNTIL '2003-09-30'
;

-- ===================================================
CREATE USER "test-nurse"
	WITH PASSWORD 'test-nurse'
	IN GROUP "gm-staff_medical", "gm-public"
	VALID UNTIL '2003-09-30'
;
CREATE USER "_test-nurse"
	WITH PASSWORD 'test-nurse'
	IN GROUP "gm-staff_medical", "_gm-staff_medical", "gm-public"
	VALID UNTIL '2003-09-30'
;

-- ===================================================
CREATE USER "test-secretary"
	WITH PASSWORD 'test-secretary'
	IN GROUP "gm-staff_office", "gm-public"
	VALID UNTIL '2003-09-30'
;
CREATE USER "_test-secretary"
	WITH PASSWORD 'test-secretary'
	IN GROUP "gm-staff_office", "_gm-staff_office", "gm-public"
	VALID UNTIL '2003-09-30'
;

-- ===================================================
-- cannot do revision tracking here since this script is (for now)
-- imported at the server level whereas revision tracking is
-- instantiated at the database level or IOW *after* this script

-- do simple schema revision tracking
--INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmTestAccounts.sql,v $', '$Revision: 1.7 $');

\set ON_ERROR_STOP 1

-- ===================================================
-- $Log: gmTestAccounts.sql,v $
-- Revision 1.7  2003-06-11 12:51:07  ncq
-- - Andreas is right, we *cannot* do revision tracking here ...
--
-- Revision 1.6  2003/06/10 08:56:59  ncq
-- - schema_revision -> gm_schema_revision
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
