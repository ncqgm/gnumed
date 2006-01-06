-- Projekt GNUmed
-- test data for regression testing lab import

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-lab_regression.sql,v $
-- $Revision: 1.23 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- identity
delete from dem.identity where
	gender = 'f'
		and
	cob = 'CA'
		and
	pk in (
		select pk_identity
		from dem.v_basic_person
		where firstnames='Laborata'
				and lastnames='Testwoman'
				and dob='1931-3-22+2:00'
	);

insert into dem.identity (gender, dob, cob, title)
values ('f', '1931-3-22+2:00', 'CA', '');

insert into dem.names (id_identity, active, lastnames, firstnames)
values (currval('dem.identity_pk_seq'), true, 'Testwoman', 'Laborata');


--delete from clin.xlnk_identity where xfk_identity = currval('dem.identity_pk_seq');

insert into clin.xlnk_identity (xfk_identity, pupic)
values (currval('dem.identity_pk_seq'), currval('dem.identity_pk_seq'));


-- encounter
insert into clin.encounter (
	fk_patient,
	fk_location,
	fk_type,
	rfe,
	aoe
) values (
	currval('dem.identity_pk_seq'),
	-1,
	(select pk from clin.encounter_type where description='chart review'),
	'first for this RFE',
	'lab regression testing'
);


-- episode
delete from clin.episode where pk in (
	select pk_episode
	from clin.v_pat_episodes
	where pk_patient = currval('dem.identity_pk_seq')
);

insert into clin.episode (
	description,
	fk_patient,
	is_open
) values (
	'lab import regression test',
	currval('dem.identity_pk_seq'),
	true
);

-- lab request
insert into clin.lab_request (
	fk_encounter,
	fk_episode,
	narrative,
	fk_test_org,
	request_id,
	fk_requestor,
	is_pending,
	request_status
) values (
	currval('clin.encounter_pk_seq'),
	currval('clin.episode_pk_seq'),
	'used for anonymized import regression tests',
	(select pk from clin.test_org where internal_name='your own practice'),
	'anon: sample ID',
	(select pk_identity from dem.v_basic_person where firstnames='Leonard Horatio' and lastnames='McCoy' and dob='1920-1-20+2:00'::timestamp),
	true,
	'pending'
);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: test_data-lab_regression.sql,v $', '$Revision: 1.23 $');

-- =============================================
-- $Log: test_data-lab_regression.sql,v $
-- Revision 1.23  2006-01-06 10:12:03  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.22  2005/12/06 13:26:55  ncq
-- - clin.clin_encounter -> clin.encounter
-- - also id -> pk
--
-- Revision 1.21  2005/12/05 19:06:38  ncq
-- - clin.clin_episode -> clin.episode
--
-- Revision 1.20  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.19  2005/09/22 15:42:38  ncq
-- - remove fk_provider
--
-- Revision 1.18  2005/09/19 16:28:23  ncq
-- - adjust to rfe/aoe
--
-- Revision 1.17  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.16  2005/03/31 20:09:32  ncq
-- - lab_request not requires non-null status
--
-- Revision 1.15  2005/03/14 14:47:37  ncq
-- - adjust to id_patient -> pk_patient
-- - add family history on Kirk's brother
--
-- Revision 1.14  2005/02/13 15:08:23  ncq
-- - add names of actors and some comments
--
-- Revision 1.13  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.12  2004/12/14 01:44:50  ihaywood
-- gmPsql now supports BEGIN..COMMIT. Note that without a "begin" it reverts
-- to the old one-line-one-transaction mode, so a lone commit is useless
-- (this is the change to test_data-lab_regression)
--
-- Revision 1.11  2004/12/06 21:11:12  ncq
-- - properly insert episode, alas, Psql.py does not support that
--   yet, psql, however, does
--
-- Revision 1.10  2004/11/28 14:38:18  ncq
-- - some more deletes
-- - use new method of episode naming
-- - this actually bootstraps again
--
-- Revision 1.9  2004/11/16 18:59:57  ncq
-- - adjust to episode naming changes
--
-- Revision 1.8  2004/09/17 21:00:18  ncq
-- - IF health issue then MUST have description
--
-- Revision 1.7  2004/09/17 20:18:10  ncq
-- - clin_episode_id_seq -> *_pk_seq
--
-- Revision 1.6  2004/06/26 23:45:51  ncq
-- - cleanup, id_* -> fk/pk_*
--
-- Revision 1.5  2004/06/26 07:33:55  ncq
-- - id_episode -> fk/pk_episode
--
-- Revision 1.4  2004/06/02 13:46:46  ncq
-- - setting default session timezone has incompatible syntax
--   across version range 7.1-7.4, henceforth specify timezone
--   directly in timestamp values, which works
--
-- Revision 1.3  2004/06/02 00:14:47  ncq
-- - add time zone setting
--
-- Revision 1.2  2004/05/30 21:03:29  ncq
-- - encounter_type.id -> encounter_type.pk
--
-- Revision 1.1  2004/05/12 23:54:37  ncq
-- - used for regression testing lab handling
--
