-- GnuMed/Archive database accounts

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/server/Attic/gmArchiveAccounts.sql,v $
-- $Id: gmArchiveAccounts.sql,v 1.1 2003-03-01 15:01:10 ncq Exp $
-- GPL
-- author: Karsten.Hilbert@gmx.net
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\unset ON_ERROR_STOP

-- remember that you usually need "user" and "_user"
-- they also need to be members of "group" and "_group", respectively
-- ===================================================
--CREATE USER "a-new-user"
--	WITH PASSWORD 'a password'
--	IN GROUP "some-group"
--	VALID UNTIL 'a timestamp'
--;
--CREATE USER "_a-new-user"
--	WITH PASSWORD 'the same password as above'
--	IN GROUP "some-group, _some-group"
--	VALID UNTIL 'a timestamp'
--;

-- ===================================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
\unset ON_ERROR_STOP
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmArchiveAccounts.sql,v $', '$Revision: 1.1 $');

\set ON_ERROR_STOP 1

-- ===================================================
-- $Log: gmArchiveAccounts.sql,v $
-- Revision 1.1  2003-03-01 15:01:10  ncq
-- - moved here from test-area/blobs_hilbert/
--
-- Revision 1.1  2003/02/02 14:26:24  ncq
-- - demonstrate account import
--
