-- Projekt GnuMed
-- test data for Dr.Leonard McCoy of Star Trek fame

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Leonard_McCoy.sql,v $
-- $Revision: 1.2 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into identity (gender, dob, cob)
values ('m', '1920-1-20', 'US');

insert into names (id_identity, active, lastnames, firstnames, title)
values (currval('identity_id_seq'), true, 'McCoy', 'Leonard', 'Dr.');

-- =============================================
-- $Log: test_data-Leonard_McCoy.sql,v $
-- Revision 1.2  2003-11-09 14:55:39  ncq
-- - update comments
--
-- Revision 1.1  2003/10/31 22:53:27  ncq
-- - started collection of test data
--
