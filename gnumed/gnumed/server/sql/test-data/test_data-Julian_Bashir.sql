-- Projekt GnuMed
-- test data for Dr.Leonard McCoy of Star Trek fame

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Julian_Bashir.sql,v $
-- $Revision: 1.4 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into identity (gender, dob, cob, title)
values ('m', '1965-11-21', 'SD', 'Dr.');

insert into names (id_identity, active, lastnames, firstnames)
values (currval('identity_id_seq'), true, 'Bashir', 'Julian');

insert into staff (fk_identity, fk_role, db_user, sign, comment)
values (
	currval('identity_id_seq'),
	(select pk from staff_role where name='doctor'),
	'test-doc',
	'JB',
	'Deep Space Nine Chief Medical Officer'
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-Julian_Bashir.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-Julian_Bashir.sql,v $', '$Revision: 1.4 $');

-- =============================================
-- $Log: test_data-Julian_Bashir.sql,v $
-- Revision 1.4  2004-01-18 21:59:06  ncq
-- - no clinical data hence no mention in xln_identity
--
-- Revision 1.3  2004/01/14 10:42:05  ncq
-- - use xlnk_identity
--
-- Revision 1.2  2004/01/10 02:01:16  ncq
-- - first <-> last name
--
-- Revision 1.1  2004/01/10 01:29:25  ncq
-- - add test data for test-nurse, test-doctor
--
