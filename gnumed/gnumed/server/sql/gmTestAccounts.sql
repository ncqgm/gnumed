-- GNUmed database test accounts

-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- !! NEVER EVER use those accounts/passwords in a  !!
-- !! production database. As they are in CVS know- !!
-- !! ledge about them is PUBLIC and thus extremely !!
-- !! insecure. DO NOT USE FOR PRODUCTION.          !!
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmTestAccounts.sql,v $
-- $Id: gmTestAccounts.sql,v 1.11 2004-07-17 20:57:53 ncq Exp $
-- GPL v2 or later
-- author: Karsten.Hilbert@gmx.net
-- ===================================================================
-- must ignore errors so we don't fail on
-- accounts that exist already

-- Anyone know a way of telling VALID UNTIL that the
-- value is CURRENT_DATE + interval '4 months' ?

-- not possible according to Tom Lane, either do in client
-- or wrap in pl/pgsql function with execute()

-- ===================================================
drop user if exists "test-doc";
CREATE USER "test-doc"
	WITH PASSWORD 'test-doc'
	IN GROUP "gm-doctors", "gm-public"
	VALID UNTIL '2004-12-31'
;

-- ===================================================
drop user if exists "test-nurse";
CREATE USER "test-nurse"
	WITH PASSWORD 'test-nurse'
	IN GROUP "gm-staff_medical", "gm-public"
	VALID UNTIL '2004-12-31'
;

-- ===================================================
drop user if exists "test-secretary";
CREATE USER "test-secretary"
	WITH PASSWORD 'test-secretary'
	IN GROUP "gm-staff_office", "gm-public"
	VALID UNTIL '2004-12-31'
;

-- ===================================================
