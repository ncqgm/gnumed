-- Projekt GnuMed
-- test data for James T. Kirk of Star Trek fame

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-James_Kirk.sql,v $
-- $Revision: 1.26 $
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
	id in (select i_id from v_basic_person where firstnames='James T.' and lastnames='Kirk' and dob='1931-3-22+2:00');

insert into identity (gender, dob, cob, title)
values ('m', '1931-3-22+2:00', 'CA', 'Capt.');

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
	select pk_episode
	from v_pat_episodes
	where id_patient = currval('identity_id_seq')
);

insert into clin_episode (id_health_issue, description)
values (
	currval('clin_health_issue_id_seq'),
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
	(select pk_staff from v_staff where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20+2:00'),
	(select pk from encounter_type where description='in surgery'),
	'first for this RFE'
);

-- diagnoses
insert into clin_aux_note (
	id_encounter,
	fk_episode,
	narrative
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'contam. w/ ext.terrest.soil'
);

insert into clin_working_diag (
	id_encounter,
	fk_episode,
	narrative,
	fk_progress_note,
	laterality,
	is_chronic,
	is_active,
	is_definite,
	is_significant
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'cut L forearm',
	currval('clin_aux_note_pk_seq'),
	'l',
	false,
	true,
	true,
	true
);

-- given Td booster shot
insert into vaccination (
	id_encounter,
	fk_episode,
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
	(select pk_staff from v_staff where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20+2:00'),
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
	fk_episode,
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
	'2000-9-17 17:33',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'inflammation screen, possibly extraterrestrial contamination',
	(select pk from test_org where internal_name='Enterprise Main Lab'),
	'EML#SC937-0176-CEC#11',
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20+2:00'::timestamp),
	'SC937-0176-CEC#15034',
	'2000-9-17 17:40',
	'2000-9-17 18:10',
	'final',
	false
);

-- results reported by lab
-- leukos
insert into test_result (
	clin_when,
	id_encounter,
	fk_episode,
	fk_type,
	val_num,
	val_unit,
	val_normal_range,
	technically_abnormal,
	material
) values (
	'2000-9-17 18:17',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	(select id from test_type where code='WBC-EML'),
	'9.5',
	'Gpt/l',
	'4.4-11.3',
	'',
	'EDTA blood'
);

insert into lnk_result2lab_req(fk_result, fk_request) values (
	currval('test_result_id_seq'),
	currval('lab_request_pk_seq')
);

-- erys
insert into test_result (
	clin_when,
	id_encounter,
	fk_episode,
	fk_type,
	val_num,
	val_unit,
	val_normal_range,
	technically_abnormal,
	material
) values (
	'2000-9-17 18:17',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	(select id from test_type where code='RBC-EML'),
	'4.40',
	'Tpt/l',
	'4.1-5.1',
	'',
	'EDTA blood'
);

insert into lnk_result2lab_req(fk_result, fk_request) values (
	currval('test_result_id_seq'),
	currval('lab_request_pk_seq')
);

-- platelets
insert into test_result (
	clin_when,
	id_encounter,
	fk_episode,
	fk_type,
	val_num,
	val_unit,
	val_normal_range,
	technically_abnormal,
	material
) values (
	'2000-9-17 18:17',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	(select id from test_type where code='PLT-EML'),
	'282',
	'Gpt/l',
	'150-450',
	'',
	'EDTA blood'
);

insert into lnk_result2lab_req(fk_result, fk_request) values (
	currval('test_result_id_seq'),
	currval('lab_request_pk_seq')
);

-- CRP
insert into test_result (
	clin_when,
	id_encounter,
	fk_episode,
	fk_type,
	val_num,
	val_unit,
	val_normal_range,
	technically_abnormal,
	material
) values (
	'2000-9-17 18:23',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	(select id from test_type where code='CRP-EML'),
	'17.3',
	'mg/l',
	'0.07-8',
	'++',
	'Serum'
);

insert into lnk_result2lab_req(fk_result, fk_request) values (
	currval('test_result_id_seq'),
	currval('lab_request_pk_seq')
);

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
	(select pk_staff from v_staff where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20+2:00'),
	(select pk from encounter_type where description='in surgery'),
	'second for this RFE'
);

-- diagnoses
insert into clin_working_diag (
	id_encounter,
	fk_episode,
	narrative,
	laterality,
	is_chronic,
	is_active,
	is_definite,
	is_significant
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'wound infection L forearm',
	'l',
	false,
	true,
	true,
	true
);

-- wound infected, penicillin had been prescribed, developed urticaria
insert into allergy (
	id_encounter,
	fk_episode,
	substance,
	allergene,
	id_type,
	narrative
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_id_seq'),
	'Penicillin V Stada',
	'Penicillin',
	1,
	'developed urticaria/dyspnoe this morning, eg. 12h after first tablet'
);

insert into allergy_state (
	fk_patient,
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-James_Kirk.sql,v $', '$Revision: 1.26 $');

-- =============================================
-- $Log: test_data-James_Kirk.sql,v $
-- Revision 1.26  2004-06-26 07:33:55  ncq
-- - id_episode -> fk/pk_episode
--
-- Revision 1.25  2004/06/02 13:46:46  ncq
-- - setting default session timezone has incompatible syntax
--   across version range 7.1-7.4, henceforth specify timezone
--   directly in timestamp values, which works
--
-- Revision 1.24  2004/06/02 00:14:46  ncq
-- - add time zone setting
--
-- Revision 1.23  2004/06/01 10:15:18  ncq
-- - fk_patient, not id_patient in allergy_state
--
-- Revision 1.22  2004/05/30 21:03:29  ncq
-- - encounter_type.id -> encounter_type.pk
--
-- Revision 1.21  2004/05/13 00:10:24  ncq
-- - test data for regression testing lab handling added
--
-- Revision 1.20  2004/05/08 17:37:08  ncq
-- - *_encounter_type -> encounter_type
--
-- Revision 1.19  2004/05/06 23:32:44  ncq
-- - internal_name now local_name
-- - technically_abnormal now text
--
-- Revision 1.18  2004/05/02 19:26:31  ncq
-- - add diagnoses
--
-- Revision 1.17  2004/04/17 11:54:16  ncq
-- - v_patient_episodes -> v_pat_episodes
--
-- Revision 1.16  2004/03/23 17:34:50  ncq
-- - support and use optionally cross-provider unified test names
--
-- Revision 1.15  2004/03/23 02:34:17  ncq
-- - fix dates on test results
-- - link test results to lab requests
--
-- Revision 1.14  2004/03/19 10:56:46  ncq
-- - allergy now has reaction -> narrative
--
-- Revision 1.13  2004/03/18 18:33:05  ncq
-- - added some lab results
--
-- Revision 1.12  2004/03/18 11:07:56  ncq
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
