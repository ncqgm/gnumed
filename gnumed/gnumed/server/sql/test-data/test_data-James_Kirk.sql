-- Projekt GnuMed
-- test data for James Tiberius Kirk of Star Trek fame

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-James_Kirk.sql,v $
-- $Revision: 1.53 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- service personalia
-- ---------------------------------------------
-- identity, should cascade to name by itself ...
delete from identity where
	gender = 'm'
		and
	cob = 'CA'
		and
	pk in (select pk_identity from v_basic_person where firstnames='James Tiberius' and lastnames='Kirk' and dob='1931-3-22+2:00');

insert into identity (gender, dob, cob, title, pupic)
values ('m', '1931-3-22+2:00', 'CA', 'Capt.', 'SFSN:SC937-0176-CEC');

insert into names (id_identity, active, lastnames, firstnames, comment)
values (currval('identity_pk_seq'), true, 'Kirk', 'James Tiberius', 'name of character in Star Trek series');

insert into names (id_identity, active, lastnames, firstnames, comment)
values (currval('identity_pk_seq'), false, 'Kirk', 'James R.', 'the original middle initial was R. as seen in "Where No Man Has Gone Before"');

insert into names (id_identity, active, lastnames, firstnames, comment)
values (currval('identity_pk_seq'), false, 'Shatner', 'William', 'name of actor in real life');

insert into enum_ext_id_types (name, issuer, context)
values ('Starfleet Serial Number', 'Star Fleet Central Staff Office', 'p');

insert into lnk_identity2ext_id (id_identity, external_id, fk_origin)
values (currval('identity_pk_seq'), 'SC937-0176-CEC', currval('enum_ext_id_types_pk_seq'));

-- only works because services are in the same database
insert into xlnk_identity (xfk_identity, pupic)
values (currval('identity_pk_seq'), currval('identity_pk_seq'));

-- =============================================
-- service BLOBs
-- =============================================
-- document of type "patient picture"
insert into doc_med (patient_id, type, comment) values (
	currval('identity_pk_seq'),
	(select pk from doc_type where name='patient photograph'),
	'Captain Kirk pictures'
);

-- image object
insert into doc_obj (doc_id, seq_idx, comment, data) VALUES (
	currval('doc_med_id_seq'),
	1,
	'a small picture of Kirk',
	'GIF89a0\\0000\\000Õ\\000\\000ÿÿÿ½\\234\\234\\224sk½\\204sÖ½µ\\224{s½\\214{¥{k\\214cR½\\234\\214{ZJ­{cÎ­\\234Æ\\224{¥sZ\\234kRcB1\\204R91!\\030çÎ½Æ­\\234cJ9µ\\204cB)\\030Z9!Î­\\224Æ¥\\214µ\\224{sR9\\214cBsZBB1!)\\030\\010ÞÆ­½¥\\21491)\\234\\204k\\214sZ\\020\\010\\000B)\\010ÖÆ­RB)cZJïçÖRJ9\\214{R­\\234kskR½­{\\214\\204Zsskkkc))!\\234\\234{\\030\\030\\020BJ!­µ\\224¥½\\23419J\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000,\\000\\000\\000\\0000\\0000\\000@\\006ÿ@\\204P¡@¼*\\220\\012çPØílP\\223I2\\032Ñ¨¬jjÄRÍX,\\020k&\\003#\\017$Òâ\\223JzÞ#§\\223Æ*)"\\217¼Å2è7\\014\\033.\\013\\007\\003\\033\\006\\015\\014(\\023!\\033\\007\\007\\002)\\022P#S#[\\020\\035\\021\\034N,B\\036\\012\\017\\016\\013{\\026\\016\\204\\011\\032\\011\\006«\\015­­\\003{°\\015%)N#\\020:¹:44\\012\\035\\020\\020\\036\\035¡\\016}{\\216$\\002%¡\\006\\003¾\\010%*P;&\\012%%\\033\\025\\237\\022^2¼4U\\022 mH\\237\\035%¢\\204\\016\\030&\\030x\\203\\006!z}ô\\013\\017\\006\\0364^33/\\0121\\000_\\2340\\021Ì\\003\\004\\014m<D\\030Ö¡a\\236\\003\\011\\022lhô S\\036\\207(2\\204\\010\\021£C\\014\\007.6\\2200\\010\\201\\003°\\012\\012^|\\222c\\203F\\033`)ÚÄ\\034ñ\\001\\234\\225p\\022¤\\2008\\001áÄ\\205ÿ._jíø`©\\2155Jr> \\024\\226''\\035\\237\\015}\\014D\\214Èª\\025\\003\\002\\011Zác1IW\\225\\004\\0070|ø cF\\011\\004\\036.\\230°ÁIÊ\\011\\017\\017\\026È\\035åGC\\210\\011\\004D4s`b\\016\\027]ºhØHH\\004\\201©\\001¯\\0268°h!\\021\\001\\002\\00140H¥AÃ+>\\013öñ;\\221\\202\\204\\210\\0348^\\000Ãà¦\\003\\002\\005\\0250\\014s´¡\\006\\011G\\204\\014\\015h*\\012B¥.*^øóÐBAI\\005\\006Sp\\030\\016áÂ\\011\\014\\034¬\\0118`h\\203Ä\\003\\016.\\016ïèÂE\\014\\021.\\036À\\200Q}ûv\\017ÃßxPÉ¦\\000\\015\\226\\022$\\200»\\222^RK÷6ú\\202ÈýaL\\015\\025\\025X|ø}\\222C~\\026/Ä!\\007\\015/ Õ\\001(\\027u\\000\\036q\\020\\010gÍ\\003\\012p\\200Á\\204<A\\000F\\012>]\\020SIo\\200 ÿÇ\\016t\\000\\007\\212\\003¢Ð\\025U\\002\\031\\210PY\\006,¢@À\\012+\\020À@\\006\\033\\0108\\230\\015\\022ÄÄFJ}=\\201\\222Cy4ÅG!\\023Ñcä\\220°Ð\\223\\037\\015\\027x0\\202\\016U\\\\\\200Àl\\036ì\\220Ânùiã\\001J%\\034`¢s`6@O,|\\034 Ô\\016Æ\\005&Á\\001¿\\014÷ \\211\\016\\024V@\\001$ ¥\\232(\\017`pÂqÁ¨pÍ \\032\\224°\\003\\010à\\214\\001ØMH\\004S\\204\\000¦ð±\\212\\227Ñuà\\200d\\013tYBC\\0159@\\202\\003\\026,ÀA\\003F\\220!\\003`^\\231QX(\\007\\224²XE\\017\\034`\\000\\001\\031Ì\\206X\\003\\226\\211¹G1\\003\\214Á\\217n>éÉS\\011\\015&¡M\\021\\010\\204"@\\001\\216<Ð\\023r\\007\\004°At$Îµ\\200\\007\\022ØÒ\\205n\\012Ô\\200C\\0150¼ÀBI\\022\\236DÄ0\\016\\234æÁ\\204\\021¤+ÿé\\003ï(Ö\\224\\010(lûÂ\\015\\212\\002\\027C\\013\\036Ü`\\022rÃùªh(Ò\\035\\224n(öDðF\\007\\034i·]w(p·]C\\034\\214§B\\203¤íë+r\\237@³Ü#\\010HØA\\005%´Ð\\202\\\\1dWLu.x\\007\\003p\\237\\020qÄ\\005J\\011ÀÖ\\023P@Á\\213z7U\\221\\2058)ð\\023F\\0118|Q\\201\\004\\025\\000tÀpþEì\\017\\004/\\234\\2113Q[\\\\q\\205\\015 \\204\\023_\\217íè¨ÂÖ*°p\\236\\004''%ÚrµNØ0\\202\\022H\\017\\227è\\007b\\021%\\201\\031¾\\036wÂ8\\020x\\221\\202Z/©]A\\005\\037\\2320ÂY\\237ÐÆÇ­\\017 Ð\\020\\002\\203LÔ\\214\\035\\021+@IKc\\005û\\206\\012ç\\015È\\002ËM\\215â¨\\001\\032\\030 Âç"dPY"0¢PY\\014)T=\\216\\2061¡ôÂ\\007\\037\\206\\030Á\\210éÄ\\026ÿ\\225\\006\\024\\020@\\001\\005+¾¸\\002\\005´\\032\\020 \\011¼\\200 !B \\237ieËÃdNæSE\\216iÁ+\\210m`!/\\036\\230PuLmD\\000\\201-/(H\\014\\234¢Xà\\234DE\\036\\202Ø\\230ô\\034PÁy\\037(ÀK\\025\\037x°ÀÇO¨0\\204¢/8`\\210\\005\\204\\220\\212\\010Tá\\234Z\\211\\011\\026±P\\200\\207v0\\202\\013xeM\\003è\\211\\011°\\205\\032\\014\\\\à\\002Á¸\\000\\010â×¨A\\014 \\031¤ð\\003=øâ\\004\\023ÀÌ+\\037Ð\\200\\003J\\002\\001k\\220è4\\227ÛZ\\016T°\\223\\023p DÑaÎù(\\200\\002\\012@Å\\001~\\031\\201\\012¼b\\203Nx¯\\205ÅzÀ1Êu¸\\003ØaJl\\032\\010ÖR@\\004\\017 @\\004/x[\\021Ép(\\033hã \\031#\\221£&Ò\\210HáªX\\016X\\206\\000¼\\005\\002\\020\\224`\\001Ö+\\\\\\012T \\203Qyÿe\\0046À ¢ q\\030­@\\207U\\007È\\000\\003|\\230*è\\200DE«XL\\003^À\\217~\\220*\\027t`\\001J|\\021\\027B\\0000R\\222²ÀF\\022\\020\\000\\006\\204\\216E¢\\023\\223b\\032 \\000:îª\\012PªB¡öf\\016tx©\\024ª\\031Æ\\000DÇ\\200\\011ÈÒ\\017¶\\022\\205\\001*p\\203}ø\\003\\004\\022\\200\\231\\006A\\0206mðÑ\\024\\216\\020\\200\\002\\2143!wü\\221S\\000L\\225b\\024 \\205kéæ\\005Í,\\032\\012j@1`\\230ãp®L¦a\\2343ÀÙ\\214¯Rm¤\\2065ý1\\202\\032ÄK\\004%\\000ÏAXé\\013"X\\020\\023\\012p@3úà¥Ä\\221Ï\\001 ð\\233$U\\220\\222Ý\\024 d$°\\015¿\\016âM¦4\\205\\011gA\\213I\\004\\006°ap§:$àN\\015jP\\002I\\222 \\004*ÙÐ\\033$t\\001ä\\020á"é\\232\\020\\007ôÐ©\\2120\\204Du.°K\\006\\\\P\\202\\030d\\000\\006\\0358\\200\\013z\\003\\214#Ð\\2138zÂ \\025»D\\010w9$:ìâ@C`°\\200\\026¤¬;\\013ÛN\\006ð¥¨à\\200ë {JAÆ6ÆÉ\\000$@\\000\\206{Ã\\013HÐ\\201\\005¸\\200\\004\\201P\\030T·\\203´ñxà[\\037(i3\\215³\\223\\212)DAçRM\\0138p\\215\\030¤A\\015-(\\031L¡\\032\\004\\000;'
);

-- =============================================
-- service historica
-- ---------------------------------------------
-- EMR data

-- put him on some vaccination schedules
delete from lnk_pat2vacc_reg where fk_patient = currval('identity_pk_seq');
-- tetanus
insert into lnk_pat2vacc_reg (fk_patient, fk_regime) values (
	currval('identity_pk_seq'),
	(select pk_regime from v_vacc_regimes where regime='Tetanus (SFCVC)')
);
-- meningococcus C
insert into lnk_pat2vacc_reg (fk_patient, fk_regime) values (
	currval('identity_pk_seq'),
	(select pk_regime from v_vacc_regimes where regime='MenC (SFCVC)')
);
-- hemophilus B
insert into lnk_pat2vacc_reg (fk_patient, fk_regime) values (
	currval('identity_pk_seq'),
	(select pk_regime from v_vacc_regimes where regime='HiB (SFCVC)')
);

-- health issue
delete from clin_health_issue where
	id_patient = currval('identity_pk_seq');

insert into clin_health_issue (id_patient, description)
values (
	currval('identity_pk_seq'),
	'9/2000 extraterrestrial infection'
);

-- episode "knife cut"
delete from clin_episode where pk in (
	select pk_episode
	from v_pat_episodes
	where pk_patient = currval('identity_pk_seq')
);

insert into clin_episode (
	description,
	fk_health_issue,
	is_open
) values (
	'postop infected laceration L forearm',
	currval('clin_health_issue_id_seq'),
	'false'::boolean
);

-- encounter: first, for knife cut ------------------------------------------------
insert into clin_encounter (
	fk_patient,
	fk_location,
	fk_provider,
	fk_type,
	started,
	last_affirmed
) values (
	currval('identity_pk_seq'),
	-1,
	(select pk_staff from v_staff where firstnames='Leonard Horatio' and lastnames='McCoy' and dob='1920-1-20+2:00'),
	(select pk from encounter_type where description='in surgery'),
	'2000-9-17 17:13',
	'2000-9-17 19:33'
);

-- RFE
insert into clin_narrative (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat,
	is_rfe
) values (
	'2000-9-17 17:14:32',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'bleeding cut forearm L',
	's',
	'true'::boolean
);

-- subjective
insert into clin_narrative (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat
) values (
	'2000-9-17 17:16:41',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'accid cut himself left forearm -2/24 w/ dirty
blade rescuing self from being tentacled,
extraterrest.envir.',
	's'
);

-- objective
insert into clin_narrative (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat
) values (
	'2000-9-17 17:20:59',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'left ulnar forearm; 6cm dirty laceration;
skin/sc fat only; musc/tend not injured; no dist sens loss;
pain/redness++; smelly secretion+; no pus',
	'o'
);

-- assessment
insert into clin_narrative (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat
) values (
	'2000-9-17 17:21:19',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'contam/infected knife cut left arm, ?extraterr. vector, needs ABs/surg/blood',
	'a'
);

-- plan
insert into clin_narrative (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat
) values (
	'2000-9-17 17:2',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'1) inflamm.screen/std ET serology
2) debridement/loose adapt.; 10ml xylocitin sc; 00-Reprolene
3) Pen 1.5 Mega 1-1-1
4) review +2/7; tomorrow if symptoms/blood screen +ve',
	'p'
);

-- AOE
insert into clin_narrative (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat,
	is_aoe
) values (
	'2000-9-17 17:14:32',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'?contaminated laceration L forearm',
	'a',
	'true'::boolean
);

-- diagnoses
insert into clin_diag (
	fk_narrative,
	laterality,
	is_chronic,
	is_active,
	is_definite,
	clinically_relevant
) values (
	currval('clin_narrative_pk_seq'),
	'l',
	false,
	true,
	true,
	true
);

-- codes
select add_coded_term (
	'?contaminated laceration L forearm',
	'T11.1',
	'ICD-10-GM 2004'
);

-- given Td booster shot
insert into vaccination (
	fk_encounter,
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
	currval('clin_episode_pk_seq'),
	'prev booster > 7 yrs',
	currval('identity_pk_seq'),
	(select pk_staff from v_staff where firstnames='Leonard Horatio' and lastnames='McCoy' and dob='1920-1-20+2:00'),
	(select id from vaccine where trade_name='Tetasorbat (SFCMS)'),
	'2000-9-17',
	'left deltoid muscle',
	'SFCMS#102041A#11'
);


-- blood sample drawn for screen/CRP
insert into lab_request (
	clin_when,
	fk_encounter,
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
	currval('clin_episode_pk_seq'),
	'inflammation screen, possibly extraterrestrial contamination',
	(select pk from test_org where internal_name='Enterprise Main Lab'),
	'EML#SC937-0176-CEC#11',
	(select pk_identity from v_basic_person where firstnames='Leonard Horatio' and lastnames='McCoy' and dob='1920-1-20+2:00'::timestamp),
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
	fk_encounter,
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
	currval('clin_episode_pk_seq'),
	(select pk from test_type where code='WBC-EML'),
	'9.5',
	'Gpt/l',
	'4.4-11.3',
	'',
	'EDTA blood'
);

insert into lnk_result2lab_req(fk_result, fk_request) values (
	currval('test_result_pk_seq'),
	currval('lab_request_pk_seq')
);

-- erys
insert into test_result (
	clin_when,
	fk_encounter,
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
	currval('clin_episode_pk_seq'),
	(select pk from test_type where code='RBC-EML'),
	'4.40',
	'Tpt/l',
	'4.1-5.1',
	'',
	'EDTA blood'
);

insert into lnk_result2lab_req(fk_result, fk_request) values (
	currval('test_result_pk_seq'),
	currval('lab_request_pk_seq')
);

-- platelets
insert into test_result (
	clin_when,
	fk_encounter,
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
	currval('clin_episode_pk_seq'),
	(select pk from test_type where code='PLT-EML'),
	'282',
	'Gpt/l',
	'150-450',
	'',
	'EDTA blood'
);

insert into lnk_result2lab_req(fk_result, fk_request) values (
	currval('test_result_pk_seq'),
	currval('lab_request_pk_seq')
);

-- CRP
insert into test_result (
	clin_when,
	fk_encounter,
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
	currval('clin_episode_pk_seq'),
	(select pk from test_type where code='CRP-EML'),
	'17.3',
	'mg/l',
	'0.07-8',
	'++',
	'Serum'
);

insert into lnk_result2lab_req(fk_result, fk_request) values (
	currval('test_result_pk_seq'),
	currval('lab_request_pk_seq')
);

-- encounter, second for knife cut ------------------------------------------
insert into clin_encounter (
	fk_patient,
	fk_location,
	fk_provider,
	fk_type,
	started,
	last_affirmed
) values (
	currval('identity_pk_seq'),
	-1,
	(select pk_staff from v_staff where firstnames='Leonard Horatio' and lastnames='McCoy' and dob='1920-1-20+2:00'),
	(select pk from encounter_type where description='in surgery'),
	'2000-9-18 8:13',
	'2000-9-18 8:47'
);

-- RFE
insert into clin_narrative (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat,
	is_rfe
) values (
	'2000-9-18 8:14:32',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'knife cut follow-up, pain/swelling',
	's',
	'true'::boolean
);

-- AOE
insert into clin_narrative (
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat,
	is_aoe
) values (
	'2000-9-18 8:17:32',
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'postop infected laceration L forearm',
	'a',
	'true'::boolean
);

-- diagnoses
insert into clin_diag (
	fk_narrative,
	laterality,
	is_chronic,
	is_active,
	is_definite,
	clinically_relevant
) values (
	currval('clin_narrative_pk_seq'),
	'l',
	false,
	true,
	true,
	true
);

-- codes
select add_coded_term (
	'postop infected laceration L forearm',
	'T79.3',
	'ICD-10-GM 2004'
);

select add_coded_term (
	'postop infected laceration L forearm',
	'B97.8!',
	'ICD-10-GM 2004'
);

-- wound infected, penicillin had been prescribed, developed urticaria
insert into allergy (
	fk_encounter,
	fk_episode,
	substance,
	allergene,
	id_type,
	narrative
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	'Penicillin V Stada',
	'Penicillin',
	1,
	'developed urticaria/dyspnoe this morning, eg. 12h after first tablet'
);

insert into allergy_state (
	fk_patient,
	has_allergy
) values (
	currval('identity_pk_seq'),
	1
);

-- =============================================
-- family history
insert into hx_family_item (
	name_relative,
	dob_relative,	
	condition,
	age_noted,
	age_of_death,
	is_cause_of_death
) values (
	'George Samuel Kirk',
	'1928-7-19+2:00',
	'Denevan neural parasite infection',
	'37 years (2267, Stardate 3287)',
	'37 years',
	true
);

insert into clin_hx_family (
	fk_encounter,
	fk_episode,
	soap_cat,
	narrative,
	fk_hx_family_item
) values (
	currval('clin_encounter_id_seq'),
	currval('clin_episode_pk_seq'),
	's',
	'brother',
	currval('hx_family_item_pk_seq')
);

insert into lnk_type2item (fk_type, fk_item) values (
	(select pk from clin_item_type where code = 'fHx'),
	currval('clin_root_item_pk_item_seq')
);

-- =============================================
-- went to Vietnam for holidays
insert into doc_med (
	patient_id,
	type,
	comment,
	ext_ref
) values (
	currval('identity_pk_seq'),
	(select pk from doc_type where name='referral report other'),
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
	currval('identity_pk_seq'),
	(select pk from doc_type where name='referral report other'),
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-James_Kirk.sql,v $', '$Revision: 1.53 $');

-- =============================================
-- $Log: test_data-James_Kirk.sql,v $
-- Revision 1.53  2005-04-08 10:01:28  ncq
-- - adapt to changed coding of narrative
--
-- Revision 1.52  2005/03/21 20:11:36  ncq
-- - adjust family history
--
-- Revision 1.51  2005/03/20 18:10:30  ncq
-- - adjust family history
--
-- Revision 1.50  2005/03/14 14:47:37  ncq
-- - adjust to id_patient -> pk_patient
-- - add family history on Kirk's brother
--
-- Revision 1.49  2005/03/01 20:42:21  ncq
-- - cleanup, basically
--
-- Revision 1.48  2005/02/20 09:46:08  ihaywood
-- demographics module with load a patient with no exceptions
--
-- Revision 1.47  2005/02/15 18:27:24  ncq
-- - test_result.id -> pk
--
-- Revision 1.46  2005/02/13 15:08:23  ncq
-- - add names of actors and some comments
--
-- Revision 1.45  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.44  2004/12/18 09:58:13  ncq
-- - vaccinate according to Starfleet rules
--
-- Revision 1.43  2004/11/28 14:38:18  ncq
-- - some more deletes
-- - use new method of episode naming
-- - this actually bootstraps again
--
-- Revision 1.42  2004/11/24 15:42:00  ncq
-- - need clin_narrative with is_episode_name *before* inserting clin_root_items
--   which signal changes since the trigger crawls v_pat_episodes for the
--   patient PK and unnamed episodes don't show up there
--
-- Revision 1.41  2004/11/21 21:01:44  ncq
-- - episode: is_active -> is_open
--
-- Revision 1.40  2004/11/16 18:59:57  ncq
-- - adjust to episode naming changes
--
-- Revision 1.39  2004/10/11 19:36:32  ncq
-- - id -> pk
--
-- Revision 1.38  2004/09/29 10:31:11  ncq
-- - test_type.id -> pk
-- - basic_unit -> conversion_unit
--
-- Revision 1.37  2004/09/25 13:25:56  ncq
-- - is_significant -> clinically_relevant
--
-- Revision 1.36  2004/09/20 21:18:26  ncq
-- - add small picture for Kirk
--
-- Revision 1.35  2004/09/17 20:32:27  ncq
-- - IF there is a health issue it MUST have a label, there is no default
--
-- Revision 1.34  2004/09/17 20:18:10  ncq
-- - clin_episode_id_seq -> *_pk_seq
--
-- Revision 1.33  2004/09/02 00:43:20  ncq
-- - add Star Fleet Staff Code as external_id
--
-- Revision 1.32  2004/08/18 08:28:56  ncq
-- - put Kirk on some vaccination schedules
--
-- Revision 1.31  2004/07/28 15:47:00  ncq
-- - improve data
--
-- Revision 1.30  2004/07/12 17:24:02  ncq
-- - code diagnoses with new structure now
--
-- Revision 1.29  2004/07/02 15:00:10  ncq
-- - bring rfe/aoe/diag/coded_diag tables/views up to snuff and use them
--
-- Revision 1.28  2004/07/02 00:28:54  ncq
-- - clin_working_diag -> clin_coded_diag + index fixes therof
-- - v_pat_diag rewritten for clin_coded_diag, more useful now
-- - v_patient_items.id_item -> pk_item
-- - grants fixed
-- - clin_rfe/aoe folded into clin_narrative, that enhanced by
--   is_rfe/aoe with appropriate check constraint logic
-- - test data adapted to schema changes
--
-- Revision 1.27  2004/06/26 23:45:50  ncq
-- - cleanup, id_* -> fk/pk_*
--
-- Revision 1.26  2004/06/26 07:33:55  ncq
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
