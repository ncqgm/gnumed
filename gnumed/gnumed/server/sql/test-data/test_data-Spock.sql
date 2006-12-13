-- Projekt GnuMed
-- test data for Mr.Spock, Enterprise
-- http://www.nimoy.com/spock.html

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Spock.sql,v $
-- $Revision: 1.12 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
insert into dem.identity (gender, dob, cob, title, pupic)
values ('m', '1931-03-26+2:00', 'US', 'Capt.', 'SFSN:S 179-276 SP');

insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (currval('dem.identity_pk_seq'), true, 'Spock', '?', 'no first name known, real vulcan name unrepresentable');

insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (currval('dem.identity_pk_seq'), false, 'Nimoy', 'Leonard', 'name of actor');

insert into clin.xlnk_identity (xfk_identity, pupic)
values (currval('dem.identity_pk_seq'), currval('dem.identity_pk_seq'));

--insert into dem.staff (fk_identity, fk_role, db_user, short_alias, comment)
--values (
--	currval('dem.identity_pk_seq'),
--	(select pk from dem.staff_role where name='doctor'),
--	'test-doc',
--	'JB',
--	'Deep Space Nine Chief Medical Officer'
--);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: test_data-Spock.sql,v $', '$Revision: 1.12 $');

-- =============================================
-- $Log: test_data-Spock.sql,v $
-- Revision 1.12  2006-12-13 11:51:33  ncq
-- - Spock does need to be in clin.xlnk_identity so that test_org can link to it
--
-- Revision 1.11  2006/01/23 22:10:57  ncq
-- - staff.sign -> .short_alias
--
-- Revision 1.10  2006/01/06 10:12:03  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.9  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.8  2005/09/19 16:38:52  ncq
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
