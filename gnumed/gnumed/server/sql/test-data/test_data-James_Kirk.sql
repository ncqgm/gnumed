-- Projekt GnuMed
-- test data for James T. Kirk of Star Trek fame

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-James_Kirk.sql,v $
-- $Revision: 1.12 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- identity
-- name
delete from names where
	firstnames = 'James T.'
		and
	lastnames = 'Kirk';

delete from identity where
	gender = 'm'
		and
	cob = 'CA'
		and
	id in (select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22');

insert into identity (gender, dob, cob, title)
values ('m', '1931-3-22', 'CA', 'Capt.');

insert into names (id_identity, active, lastnames, firstnames)
values (currval('identity_id_seq'), true, 'Kirk', 'James T.');

insert into xlnk_identity (xfk_identity, pupic)
values (currval('identity_id_seq'), currval('identity_id_seq'));

-- default health issue
delete from clin_health_issue where
	id_patient = currval('identity_id_seq');

insert into clin_health_issue (id_patient)
values (currval('identity_id_seq'));

-- episode "knive cut"
delete from clin_episode where id in (
	select id_episode
	from v_patient_episodes
	where id_patient = currval('identity_id_seq')
);

insert into clin_episode (id_health_issue, description)
values (
	(select id
	 from clin_health_issue
	 where
	 	id_patient=currval('identity_id_seq')
			and
		description = 'xxxDEFAULTxxx'),
	'knive cut left arm 9/2000'
);

-- encounter: first, for knive cut ------------------------------------------------
insert into clin_encounter (
	fk_patient,
	fk_location,
	fk_provider,
	fk_type,
	description
) values (
	currval('identity_id_seq'),
	-1,
	(select pk_staff from v_staff where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20'),
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
	clin_when,
	site,
	batch_no
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'contaminated knife cut, prev booster > 7 yrs',
	currval('identity_id_seq'),
	(select pk_staff from v_staff where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20'),
	(select id from vaccine where trade_name='Tetasorbat SSW'),
	'2000-9-17',
	'left deltoid muscle',
	'102041A'
);

insert into lnk_vacc2vacc_def (
	fk_vaccination,
	fk_vacc_def
) values (
	currval('vaccination_id_seq'),
	(select id
	 from vacc_def
	 where
	 	fk_regime=(select id from vacc_regime where name='Tetanus (STIKO)')
			and
		is_booster
	)
);

-- blood sample drawn for screen/CRP
insert into lab_request (
	clin_when,
	id_encounter,
	id_episode,
	narrative,
	fk_test_org,
	request_id,
	fk_requestor,
	lab_request_id,
	lab_rxd_when,
	results_reported_when,
	request_status,
	is_pending
) values (
	'2000-9-17',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'inflammation screen, possibly extraterrestrial contamination',
	(select pk from test_org where internal_name='Enterprise Main Lab'),
	'EML#SC937-0176-CEC#11',
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20'::timestamp),
	'SC937-0176-CEC#15034',
	'2000-9-17',
	'2000-9-17',
	'final',
	false
);

-- results reported by lab


-- encounter, second for knive cut ------------------------------------------
insert into clin_encounter (
	fk_patient,
	fk_location,
	fk_provider,
	fk_type,
	description
) values (
	currval('identity_id_seq'),
	-1,
	(select pk_staff from v_staff where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20'),
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
	currval('identity_id_seq'),
	1
);




-- went to Vietnam for holidays
insert into doc_med (
	patient_id,
	type,
	comment,
	ext_ref
) values (
	currval('identity_id_seq'),
	(select id from doc_type where name='referral report other'),
	'Vietnam 2003: The Peoples Republic',
	'vietnam-2003-3::1'
);

insert into doc_desc (
	doc_id,
	text
) values (
	currval('doc_med_id_seq'),
	'people'
);

-- need to run the insert on data separately !
insert into doc_obj (
	doc_id,
	seq_idx,
	comment
) values (
	currval('doc_med_id_seq'),
	1,
	'Happy schoolgirls enjoying the afternoon sun catching the smile of
	 passers-by at an ancient bridge in the paddy fields near Hue.'
);

insert into doc_obj (
	doc_id,
	seq_idx,
	comment
) values (
	currval('doc_med_id_seq'),
	2,
	'Mekong River Delta Schoolgirls making their way home.'
);

insert into doc_med (
	patient_id,
	type,
	comment,
	ext_ref
) values (
	currval('identity_id_seq'),
	(select id from doc_type where name='referral report other'),
	'Vietnam 2003: Tagwerk',
	'vietnam-2003-3::2'
);

insert into doc_desc (
	doc_id,
	text
) values (
	currval('doc_med_id_seq'),
	'life'
);

-- need to run the insert on data separately !
insert into doc_obj (
	doc_id,
	seq_idx,
	comment
) values (
	currval('doc_med_id_seq'),
	1,
	'Perfume pagoda river boating'
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '%James_Kirk%';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-James_Kirk.sql,v $', '$Revision: 1.12 $');

-- =============================================
-- $Log: test_data-James_Kirk.sql,v $
-- Revision 1.12  2004-03-18 11:07:56  ncq
-- - fix integrity violations
--
-- Revision 1.11  2004/03/18 10:57:20  ncq
-- - several fixes to the data
-- - better constraints on vacc.seq_no/is_booster
--
-- Revision 1.10  2004/01/15 14:52:10  ncq
-- - fix id_patient breakage
--
-- Revision 1.9  2004/01/14 10:42:05  ncq
-- - use xlnk_identity
--
-- Revision 1.8  2004/01/06 23:44:40  ncq
-- - __default__ -> xxxDEFAULTxxx
--
-- Revision 1.7  2003/12/29 16:06:10  uid66147
-- - adjust to new tables: use fk_provider, lnk_vacc2vacc_def
-- - add document BLOBs (data needs to be imported separately)
--
-- Revision 1.6  2003/11/27 00:18:47  ncq
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
