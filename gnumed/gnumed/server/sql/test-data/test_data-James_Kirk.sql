-- Projekt GnuMed
-- test data for James T. Kirk of Star Trek fame

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-James_Kirk.sql,v $
-- $Revision: 1.6 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
begin;

-- identity
delete from identity where
	gender = 'm'
		and
	cob = 'CA'
		and
	id in (select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22');

insert into identity (gender, dob, cob, title)
values ('m', '1931-3-22', 'CA', 'Capt.');

-- name
delete from names where
	firstnames = 'James T.'
		and
	lastnames = 'Kirk';

insert into names (id_identity, active, lastnames, firstnames)
values (currval('identity_id_seq'), true, 'Kirk', 'James T.');

-- health issue
delete from clin_health_issue where
	id_patient = (select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22');

insert into clin_health_issue (id_patient)
values ((select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22'));

-- episode
delete from clin_episode where
	id in (select id_episode
			from v_patient_episodes
			where id_patient=(select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22'));

insert into clin_episode (id_health_issue, description)
values (
	(select id from clin_health_issue where
		id_patient=(select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22')
			and
		description = '__default__'),
	'knive cut left forearm 9/2000'
);

-- encounter: first, for knive cut
insert into clin_encounter (
	fk_patient,
	fk_location,
	fk_provider,
	fk_type,
	description
) values (
	(select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22'),
	-1,
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20'),
	(select id from _enum_encounter_type where description='in surgery'),
	'first for this RFE'
);

-- given Td booster shot
insert into vaccination (
	id_encounter,
	id_episode,
	narrative,
	fk_patient,
	fk_provider,
	fk_vaccine,
	fk_vacc_def,
	clin_when,
	site,
	batch_no
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'for contaminated knife cut and previous booster > 7 years old',
	(select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22'),
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20'),
	(select id from vaccine where trade_name='Tetasorbat SSW'),
	(select id from vacc_def where
		fk_regime = (select id from vacc_regime where fk_indication=(select id from vacc_indication where description='tetanus'))
			and
		is_booster = true
	),
	'2000-9-17',
	'left deltoid muscle',
	'102041A'
);

-- encounter
insert into clin_encounter (
	fk_patient,
	fk_location,
	fk_provider,
	fk_type,
	description
) values (
	(select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22'),
	-1,
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20'),
	(select id from _enum_encounter_type where description='in surgery'),
	'second for this RFE'
);

-- wound infected, penicillin had been prescribed, developed urticaria
insert into allergy (
	id_encounter,
	id_episode,
	substance,
	allergene,
	id_type,
	reaction
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'Penicillin V Stada',
	'Penicillin',
	1,
	'developed urticaria/dyspnoe this morning, eg. 12h after first tablet'
);

insert into allergy_state (
	id_patient,
	has_allergy
) values (
	(select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22'),
	1
);

commit;
-- =============================================
-- $Log: test_data-James_Kirk.sql,v $
-- Revision 1.6  2003-11-27 00:18:47  ncq
-- - vacc_def links to vacc_regime now
--
-- Revision 1.5  2003/11/23 23:35:11  ncq
-- - names.title -> identity.title
--
-- Revision 1.4  2003/11/16 19:32:17  ncq
-- - clin_when in clin_root_item
--
-- Revision 1.3  2003/11/13 09:47:29  ncq
-- - use clin_date instead of date_given in vaccination
--
-- Revision 1.2  2003/11/09 17:58:46  ncq
-- - add an allergy
--
-- Revision 1.1  2003/10/31 22:53:27  ncq
-- - started collection of test data
--
