-- Projekt GnuMed
-- test data for Mr.Spock, Enterprise
-- http://www.nimoy.com/spock.html

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Spock.sql,v $
-- $Revision: 1.8 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into identity (gender, dob, cob, title, pupic)
values ('m', '1931-03-26+2:00', 'US', 'Capt.', 'SFSN:S 179-276 SP');

insert into names (id_identity, active, lastnames, firstnames, comment)
values (currval('identity_pk_seq'), true, 'Spock', '?', 'no first name known, real vulcan name unrepresentable');

insert into names (id_identity, active, lastnames, firstnames, comment)
values (currval('identity_pk_seq'), false, 'Nimoy', 'Leonard', 'name of actor');

insert into xlnk_identity (xfk_identity, pupic)
values (currval('identity_pk_seq'), currval('identity_pk_seq'));

--insert into staff (fk_identity, fk_role, db_user, sign, comment)
--values (
--	currval('identity_pk_seq'),
--	(select pk from staff_role where name='doctor'),
--	'test-doc',
--	'JB',
--	'Deep Space Nine Chief Medical Officer'
--);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-Spock.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-Spock.sql,v $', '$Revision: 1.8 $');

-- =============================================
-- $Log: test_data-Spock.sql,v $
-- Revision 1.8  2005-09-19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.7  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.6  2005/02/13 15:08:23  ncq
-- - add names of actors and some comments
--
-- Revision 1.5  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.4  2004/06/02 13:46:46  ncq
-- - setting default session timezone has incompatible syntax
--   across version range 7.1-7.4, henceforth specify timezone
--   directly in timestamp values, which works
--
-- Revision 1.3  2004/06/02 00:14:47  ncq
-- - add time zone setting
--
-- Revision 1.2  2004/03/18 10:58:57  ncq
-- - xlnk_id
--
-- Revision 1.1  2004/03/18 10:24:10  ncq
-- - added Mr.Spock
--
