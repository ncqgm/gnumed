-- Projekt GnuMed
-- test data for Dr.Leonard McCoy of Star Trek fame

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Leonard_McCoy.sql,v $
-- $Revision: 1.6 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into identity (gender, dob, cob, title)
values ('m', '1920-1-20', 'US', 'Dr.');

insert into names (id_identity, active, lastnames, firstnames)
values (currval('identity_id_seq'), true, 'McCoy', 'Leonard');

insert into xlnk_identity (xfk_identity, pupic)
values (currval('identity_id_seq'), currval('identity_id_seq'));

insert into staff (fk_identity, fk_role, db_user, sign, comment)
values (
	currval('identity_id_seq'),
	(select pk from staff_role where name='doctor'),
	'any-doc',
	'LMcC',
	'Enterprise Chief Medical Officer'
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-Leonard_McCoy.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-Leonard_McCoy.sql,v $', '$Revision: 1.6 $');

-- =============================================
-- $Log: test_data-Leonard_McCoy.sql,v $
-- Revision 1.6  2004-01-14 10:42:05  ncq
-- - use xlnk_identity
--
-- Revision 1.5  2004/01/10 01:29:25  ncq
-- - add test data for test-nurse, test-doctor
--
-- Revision 1.4  2003/12/29 16:07:19  uid66147
-- - institute as staff member
--
-- Revision 1.3  2003/11/23 23:35:11  ncq
-- - names.title -> identity.title
--
-- Revision 1.2  2003/11/09 14:55:39  ncq
-- - update comments
--
-- Revision 1.1  2003/10/31 22:53:27  ncq
-- - started collection of test data
--
