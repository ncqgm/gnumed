-- Projekt GnuMed
-- test data for Mr.Spock, Enterprise
-- http://www.nimoy.com/spock.html

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Spock.sql,v $
-- $Revision: 1.3 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
set time zone '+2:00';

insert into identity (gender, dob, cob, title)
values ('m', '1931-03-26', 'US', 'Capt.');

insert into names (id_identity, active, lastnames, firstnames)
values (currval('identity_id_seq'), true, 'Spock', 'Leonard');

insert into xlnk_identity (xfk_identity, pupic)
values (currval('identity_id_seq'), currval('identity_id_seq'));

--insert into staff (fk_identity, fk_role, db_user, sign, comment)
--values (
--	currval('identity_id_seq'),
--	(select pk from staff_role where name='doctor'),
--	'test-doc',
--	'JB',
--	'Deep Space Nine Chief Medical Officer'
--);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-Spock.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-Spock.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: test_data-Spock.sql,v $
-- Revision 1.3  2004-06-02 00:14:47  ncq
-- - add time zone setting
--
-- Revision 1.2  2004/03/18 10:58:57  ncq
-- - xlnk_id
--
-- Revision 1.1  2004/03/18 10:24:10  ncq
-- - added Mr.Spock
--
