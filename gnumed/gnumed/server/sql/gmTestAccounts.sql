-- GnuMed database test accounts

-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- !! NEVER EVER use those accounts/passwords in a  !!
-- !! production database. As they are in CVS know- !!
-- !! ledge about them is PUBLIC and thus extremely !!
-- !! insecure. DO NOT USE FOR PRODUCTION.          !!
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmTestAccounts.sql,v $
-- $Id: gmTestAccounts.sql,v 1.2 2003-01-20 12:11:46 ncq Exp $
-- GPL
-- author: Karsten.Hilbert@gmx.net
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\unset ON_ERROR_STOP

-- ===================================================
CREATE USER "test-doc"
	WITH PASSWORD 'test-doc'
	IN GROUP "gm-doctors, gm-public"
	VALID UNTIL (CURRENT_DATE + interval '4 months')
;
CREATE USER "_test-doc"
	WITH PASSWORD 'test-doc'
	IN GROUP "gm-doctors, _gm-doctors, gm-public"
	VALID UNTIL (CURRENT_DATE + interval '4 months')
;

-- ===================================================
CREATE USER "test-nurse"
	WITH PASSWORD 'test-nurse'
	IN GROUP "gm-staff_medical, gm-public"
	VALID UNTIL (CURRENT_DATE + interval '4 months')
;
CREATE USER "_test-nurse"
	WITH PASSWORD 'test-nurse'
	IN GROUP "gm-staff_medical, _gm-staff_medical, gm-public"
	VALID UNTIL (CURRENT_DATE + interval '4 months')
;

-- ===================================================
CREATE USER "test-secretary"
	WITH PASSWORD 'test-secretary'
	IN GROUP "gm-staff_office, gm-public"
	VALID UNTIL (CURRENT_DATE + interval '4 months')
;
CREATE USER "_test-secretary"
	WITH PASSWORD 'test-secretary'
	IN GROUP "gm-staff_office, _gm-staff_office, gm-public"
	VALID UNTIL (CURRENT_DATE + interval '4 months')
;

-- ===================================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmTestAccounts.sql,v $', '$Revision: 1.2 $');

\set ON_ERROR_STOP 1

-- ===================================================
-- $Log: gmTestAccounts.sql,v $
-- Revision 1.2  2003-01-20 12:11:46  ncq
-- - typo
--
-- Revision 1.1  2003/01/19 15:30:32  ncq
-- - a few test users
--
