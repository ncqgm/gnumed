-- Projekt GnuMed
-- test data for Enterprise Nurse Christine Chapel

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Christine_Chapel.sql,v $
-- $Revision: 1.2 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into identity (gender, dob, cob, title)
values ('f', '1932-2-23', 'US', 'Dr.RN');

insert into names (id_identity, active, lastnames, firstnames)
values (currval('identity_id_seq'), true, 'Chapel', 'Christine');

insert into staff (fk_identity, fk_role, db_user, sign, comment)
values (
	currval('identity_id_seq'),
	(select pk from staff_role where name='nurse'),
	'test-nurse',
	'CC',
	'Enterprise Head Nurse, temporarily Enterprise Chief Medical Officer'
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-Christine_Chapel.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-Christine_Chapel.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: test_data-Christine_Chapel.sql,v $
-- Revision 1.2  2004-01-10 02:00:44  ncq
-- - first names <-> last names
--
-- Revision 1.1  2004/01/10 01:29:25  ncq
-- - add test data for test-nurse, test-doctor
--
