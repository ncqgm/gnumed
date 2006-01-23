-- Projekt GnuMed
-- test data for Dr.Leonard Horatio McCoy of Star Trek fame

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-Leonard_McCoy.sql,v $
-- $Revision: 1.19 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
delete from dem.identity where
	gender = 'm'
		and
	cob = 'US'
		and
	pk in (
		select pk_identity
		from dem.v_basic_person
		where firstnames='Leonard Horatio'
				and lastnames='McCoy'
				and dob='1920-1-20+2:00'
	);

insert into dem.identity (gender, dob, cob, title)
values ('m', '1920-1-20+2:00', 'US', 'Dr.');

insert into dem.names (id_identity, active, lastnames, firstnames)
values (currval('dem.identity_pk_seq'), true, 'McCoy', 'Leonard Horatio');

insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (currval('dem.identity_pk_seq'), false, 'DeForest', 'Kelley', 'name of the actor');

delete from clin.xlnk_identity where xfk_identity = currval('dem.identity_pk_seq');

insert into clin.xlnk_identity (xfk_identity, pupic)
values (currval('dem.identity_pk_seq'), currval('dem.identity_pk_seq'));

insert into blobs.xlnk_identity (xfk_identity, pupic)
values (currval('dem.identity_pk_seq'), currval('dem.identity_pk_seq'));

insert into dem.staff (fk_identity, fk_role, db_user, short_alias, comment)
values (
	currval('dem.identity_pk_seq'),
	(select pk from dem.staff_role where name='doctor'),
	'any-doc',
	'LMcC',
	'Enterprise Chief Medical Officer'
);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: test_data-Leonard_McCoy.sql,v $', '$Revision: 1.19 $');

-- =============================================
-- $Log: test_data-Leonard_McCoy.sql,v $
-- Revision 1.19  2006-01-23 22:10:57  ncq
-- - staff.sign -> .short_alias
--
-- Revision 1.18  2006/01/06 10:12:03  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.17  2005/12/04 09:49:26  ncq
-- - register in blobs.xlnk_identity so blobs.doc_obj.fk_intended_reviewer works
--
-- Revision 1.16  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.15  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.14  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.13  2005/02/13 15:08:23  ncq
-- - add names of actors and some comments
--
-- Revision 1.12  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.11  2004/11/28 14:38:18  ncq
-- - some more deletes
-- - use new method of episode naming
-- - this actually bootstraps again
--
-- Revision 1.10  2004/06/02 13:46:46  ncq
-- - setting default session timezone has incompatible syntax
--   across version range 7.1-7.4, henceforth specify timezone
--   directly in timestamp values, which works
--
-- Revision 1.9  2004/06/02 00:14:47  ncq
-- - add time zone setting
--
-- Revision 1.8  2004/03/18 10:59:24  ncq
-- - xlnk_id
--
-- Revision 1.7  2004/01/18 21:59:06  ncq
-- - no clinical data hence no mention in xln_identity
--
-- Revision 1.6  2004/01/14 10:42:05  ncq
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
