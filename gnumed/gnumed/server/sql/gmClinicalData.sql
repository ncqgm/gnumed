-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalData.sql,v $
-- $Id: gmClinicalData.sql,v 1.44 2006-02-08 15:15:39 ncq Exp $
-- license: GPL
-- author: Ian Haywood, Horst Herb

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
--		self.__consultation_types = [
--			_('in surgery'),
--			_('home visit'),
--			_('by phone'),
--			_('at specialist'),
--			_('patient absent'),
--			_('by email'),
--			_('other consultation')
--		]
INSERT INTO clin.encounter_type (description) values (i18n.i18n('in surgery'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('phone consultation'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('fax consultation'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('home visit'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('nursing home visit'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('repeat script'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('hospital visit'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('video conference'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('proxy encounter'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('emergency encounter'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('chart review'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('other encounter'));

-- ===================================================================
insert into clin._enum_allergy_type (value) values (i18n.i18n('allergy'));
insert into clin._enum_allergy_type (value) values (i18n.i18n('sensitivity'));

-- ===================================================================
-- soap cat ranking for sorting
insert into clin.soap_cat_ranks (rank, soap_cat) values (1, 's');
insert into clin.soap_cat_ranks (rank, soap_cat) values (2, 'o');
insert into clin.soap_cat_ranks (rank, soap_cat) values (3, 'a');
insert into clin.soap_cat_ranks (rank, soap_cat) values (4, 'p');

-- ===================================================================
-- v_emr_journal
select i18n.i18n('RFE');

select i18n.i18n('health issue');
select i18n.i18n('noted at age');
select i18n.i18n('episode');
select i18n.i18n('encounter');

select i18n.i18n('vaccine');
select i18n.i18n('batch no');
select i18n.i18n('indication');
select i18n.i18n('site');
select i18n.i18n('notes');

select i18n.i18n('allergene');
select i18n.i18n('substance');
select i18n.i18n('generic');
select i18n.i18n('ATC code');
select i18n.i18n('type');
select i18n.i18n('reaction');

select i18n.i18n('lab');
select i18n.i18n('sample ID');
select i18n.i18n('sample taken');
select i18n.i18n('status');
select i18n.i18n('notes');

select i18n.i18n('code');
select i18n.i18n('name');
select i18n.i18n('value');

-- ===================================================================
-- clinical narrative types
-- * history types
insert into clin.clin_item_type (code, type) values (i18n.i18n('HxRFE'), i18n.i18n('history of presenting complaint'));
insert into clin.clin_item_type (code, type) values (i18n.i18n('psHx'), i18n.i18n('psycho-social history'));
insert into clin.clin_item_type (code, type) values (i18n.i18n('fHx'),  i18n.i18n('family history'));
insert into clin.clin_item_type (code, type) values (i18n.i18n('sxHx'), i18n.i18n('sexual history'));

-- * social history subtypes
insert into clin.clin_item_type (code, type) values (i18n.i18n('sHxD'), i18n.i18n('diet'));
insert into clin.clin_item_type (code, type) values (i18n.i18n('sHxH'), i18n.i18n('housing'));
-- insert into clin.clin_item_type (code, type) values (i18n.i18n(''), i18n.i18n(''));

-- Eigenanamnese/Fremdanamnese ??, Familienanamnese, Sozialanamnese, Allg./vegetat. Anamnese

-- Social history - my working definition -- courtesy of Elizabeth Dodd
-- A collection of information about lifestyle, culture, behaviour of an
-- individual which assists the doctor with assessment of disease risk for this
-- individual and the effect of disease on this individual.
-- Some is collected for legal and administrative needs and this varies in each
-- country.

-- Ethnicity
-- Immigrant status - year
-- - - ? interned
-- - - country of birth
-- - - reasons for move (economic, religious, family, war)
-- Housing (house, flat, caravan, shack, tent, natural shelter, group
-- accommodation)
-- Family type in dwelling (Nuclear family, 3 generation family, multiple adults)
-- Education ( primary, secondary, tertiary) total years of schooling if less than 10
-- Language used at home
-- Jobs - past and present
-- Actual place of work
-- If ever in prison
-- Drug use
-- method of administration (intravenous, smoking, oral, sniffed)
-- substances used (tobacco, alcohol, THC, amphetamines, ecstacy, kava and other!)
-- Retired /Jobseeking/ Not in regular Workforce/ Subsistence existence/ Not cash economy/ work from home/ social security benefit recipient
-- Leisure activities
-- Sporting activities (past and present)
-- Marital status/ Sexuality
-- and a link to spouse´s name, type of work, ethnicity
-- Dependents
-- Diet
-- Religion
-- War Service (conflict, type of service eg navy, guerilla)
-- Political affiliation
-- Does another individual deal with this person's financial affairs (legal or
-- informal arrangement)
-- Does another individual deal with this person's medical decisions? (legal or informal arrangement)
-- This person's goals for their own life - usually recorded along the way in
-- progress notes. eg studying medicine,

-- demographics (?):
-- - occupational history
-- - educational level
-- - ethnicity 
--   country of birth
--   first language
--   language spoken at home
--   local dominant language proficiency
--   AU statistics bureau
--   ISO lang/country

-- ===================================================================
--INSERT INTO clin._enum_hx_type (description) values (i18n.i18n('presenting complaint'));
--INSERT INTO clin._enum_hx_type (description) values (i18n.i18n('history of present illness'));
--INSERT INTO clin._enum_hx_type (description) values (i18n.i18n('drug'));
--INSERT INTO clin._enum_hx_type (description) values (i18n.i18n('other'));

-- ===================================================================
--insert into clin._enum_hx_source (description) values (i18n.i18n('patient'));
--insert into clin._enum_hx_source (description) values (i18n.i18n('clinician'));
--insert into clin._enum_hx_source (description) values (i18n.i18n('relative'));
--insert into clin._enum_hx_source (description) values (i18n.i18n('carer'));
--insert into clin._enum_hx_source (description) values (i18n.i18n('notes'));
--insert into clin._enum_hx_source (description) values (i18n.i18n('correspondence'));

-- ===================================================================
--INSERT INTO enum_coding_systems (description) values (i18n.i18n('general'));
--INSERT INTO enum_coding_systems (description) values (i18n.i18n('clinical'));
--INSERT INTO enum_coding_systems (description) values (i18n.i18n('diagnosis'));
--INSERT INTO enum_coding_systems (description) values (i18n.i18n('therapy'));
--INSERT INTO enum_coding_systems (description) values (i18n.i18n('pathology'));
--INSERT INTO enum_coding_systems (description) values (i18n.i18n('bureaucratic'));
--INSERT INTO enum_coding_systems (description) values (i18n.i18n('ean'));
--INSERT INTO enum_coding_systems (description) values (i18n.i18n('other'));

-- ===================================================================
--INSERT INTO enum_confidentiality_level (description) values (i18n.i18n('public'));
--INSERT INTO enum_confidentiality_level (description) values (i18n.i18n('relatives'));
--INSERT INTO enum_confidentiality_level (description) values (i18n.i18n('receptionist'));
--INSERT INTO enum_confidentiality_level (description) values (i18n.i18n('clinical staff'));
--INSERT INTO enum_confidentiality_level (description) values (i18n.i18n('doctors'));
--INSERT INTO enum_confidentiality_level (description) values (i18n.i18n('doctors of practice only'));
--INSERT INTO enum_confidentiality_level (description) values (i18n.i18n('treating doctor'));

-- ===================================================================
-- measurements stuff

-- request status strings
select i18n.i18n('pending');
select i18n.i18n('preliminary');
select i18n.i18n('partial');
select i18n.i18n('final');


delete from clin.test_org;

-- various "organizations" taking measurements
-- patient taking measurements herself
insert into clin.test_org (fk_org, internal_name, comment) values (
	-1,
	i18n.i18n('patient'),
	'self-measurement as reported by patient'
);

-- if you want to be lazy and just link all external results to one fake providing lab
insert into clin.test_org (fk_org, internal_name, comment) values (
	-2,
	i18n.i18n('external org'),
	'any external organization, regardless
	 of real source for measurements'
);

-- your own practice as a test-providing org
insert into clin.test_org (fk_org, internal_name, comment) values (
	-3,
	i18n.i18n('your own practice'),
	'for inhouse lab/tests/measurements'
);

-- measurement definitions
-- weight
insert into clin.test_type (
	fk_test_org, code, coding_system, name, comment, conversion_unit
) values (
	currval('clin.test_org_pk_seq'),
	i18n.i18n('wght'),
	null,
	i18n.i18n('weight (body mass)'),
	i18n.i18n('the patient''s weight (body mass to be accurate)'),
	'kg'
);
-- height
insert into clin.test_type (
	fk_test_org, code, coding_system, name, comment, conversion_unit
) values (
	currval('clin.test_org_pk_seq'),
	i18n.i18n('hght'),
	null,
	i18n.i18n('height'),
	i18n.i18n('lying in infants, else standing, see result notes'),
	'm'
);
-- blood pressure
-- manually/by device, sitting/lying/standing, Riva-Rocci vs. other methods handled in result specifics
insert into clin.test_type (
	fk_test_org, code, coding_system, name, comment, conversion_unit
) values (
	currval('clin.test_org_pk_seq'),
	i18n.i18n('RR'),
	null,
	i18n.i18n('blood pressure'),
	i18n.i18n('specifics attached to result record'),
	'Pa'
);
-- pulse
insert into clin.test_type (
	fk_test_org, code, coding_system, name, comment, conversion_unit
) values (
	currval('clin.test_org_pk_seq'),
	i18n.i18n('pulse'),
	null,
	i18n.i18n('pulse, periph.art.'),
	i18n.i18n('peripheral arterial pulse'),
	'Hz'
);
-- peripheral arterial oxygenation
insert into clin.test_type (
	fk_test_org, code, coding_system, name, comment, conversion_unit
) values (
	currval('clin.test_org_pk_seq'),
	i18n.i18n('SpO2'),
	null,
	i18n.i18n('blood oxygen saturation'),
	i18n.i18n('peripheral arterial blood oxygenization level, transduced'),
	'%'
);
--insert into clin.test_type (
--	fk_test_org, code, coding_system, name, comment, conversion_unit
--) values (
--	currval('clin.test_org_pk_seq'),
--	i18n.i18n('code'),
--	null,
--	i18n.i18n('name'),
--	i18n.i18n('comment'),
--	'unit'
--);

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalData.sql,v $', '$Revision: 1.44 $');

-- =============================================
-- $Log: gmClinicalData.sql,v $
-- Revision 1.44  2006-02-08 15:15:39  ncq
-- - factor our vaccination stuff into its own set of files
-- - remove clin.lnk_vacc_ind2code in favour of clin.coded_term usage
-- - improve comments as discussed on the list
--
-- Revision 1.43  2006/01/09 13:46:19  ncq
-- - adjust to schema "i18n" qualification
--
-- Revision 1.42  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.41  2006/01/01 17:57:14  ncq
-- - add vaccination indications
--
-- Revision 1.40  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.39  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.38  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.37  2005/05/17 08:13:49  ncq
-- - prepare "RFE" for translation
--
-- Revision 1.36  2005/05/08 21:50:42  ncq
-- - ranking only makes sense if ranks are different :-)
--
-- Revision 1.35  2005/04/17 16:31:34  ncq
-- - added some strings
--
-- Revision 1.34  2005/03/31 18:02:07  ncq
-- - add more strings for translation
--
-- Revision 1.33  2005/03/31 17:42:43  ncq
-- - soap_cat_ranks, request_status strings
--
-- Revision 1.32  2004/09/29 10:26:40  ncq
-- - basic_unit -> conversion_unit
--
-- Revision 1.31  2004/09/25 13:23:32  ncq
-- - add dummy test orgs for in-house/self-measured/generic external
--
-- Revision 1.30  2004/07/18 11:50:19  ncq
-- - added arbitrary typing of clin_root_items
--
-- Revision 1.29  2004/07/05 18:52:26  ncq
-- - no data for _enum_hx_type needed anymore
--
-- Revision 1.28  2004/05/08 17:37:08  ncq
-- - *_encounter_type -> encounter_type
--
-- Revision 1.27  2004/05/04 09:10:59  ncq
-- - fix your own lab test org
--
-- Revision 1.26  2004/05/04 08:43:28  ncq
-- - meaningful data for test_org "your own practice"
--
-- Revision 1.25  2004/04/30 12:22:31  ihaywood
-- new referral table
-- some changes to old medications tables, but still need more work
--
-- Revision 1.24  2004/04/21 15:35:23  ihaywood
-- new referral table (do we still need gmclinical.form_data then?)
--
-- Revision 1.23  2004/03/18 10:57:20  ncq
-- - several fixes to the data
-- - better constraints on vacc.seq_no/is_booster
--
-- Revision 1.22  2004/03/12 23:15:04  ncq
-- - adjust to id_ -> fk_/pk_
--
-- Revision 1.21  2004/02/18 14:08:29  ncq
-- - add "chart review" encounter type
--
-- Revision 1.20  2004/01/22 23:44:39  ncq
-- - add FSME
--
-- Revision 1.19  2004/01/10 01:29:25  ncq
-- - add test data for test-nurse, test-doctor
--
-- Revision 1.18  2003/12/29 15:29:45  uid66147
-- - staff roles data
-- - more vacc_indications
-- - more vacc_indications -> disease codes
--
-- Revision 1.17  2003/11/22 14:54:33  ncq
-- - add HepA vaccination indication
--
-- Revision 1.16  2003/11/17 11:14:53  sjtan
--
-- (perhaps temporary) extra referencing table for past history.
--
-- Revision 1.15  2003/11/02 10:17:02  ihaywood
-- fixups that crash psql.py
--
-- Revision 1.14  2003/10/26 09:41:03  ncq
-- - truncate -> delete from
--
-- Revision 1.13  2003/10/21 15:04:48  ncq
-- - update vaccination schedules for Germany
--
-- Revision 1.12  2003/10/19 12:58:58  ncq
-- - add vacc route data
--
-- Revision 1.11  2003/08/13 14:31:29  ncq
-- - add some test tyes
--
-- Revision 1.10  2003/07/27 21:57:34  ncq
-- - comment out *semantic* type of coding system ... (what was that intended for anyways?)
--
-- Revision 1.9  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.8  2003/05/05 12:44:33  ncq
-- - table databases does not exist anymore
--
-- Revision 1.7  2003/05/04 23:59:35  ncq
-- - add comment on encounter types
--
-- Revision 1.6  2003/04/28 20:56:16  ncq
-- - unclash "allergy" in hx type and type of allergic reaction + translations
-- - some useful indices
--
-- Revision 1.5  2003/04/25 13:05:49  ncq
-- - adapt to frontend hookup for encounter types
--
-- Revision 1.4  2003/04/12 15:43:17  ncq
-- - adapted to new gmclinical.sql
--
-- Revision 1.3  2003/04/09 13:50:29  ncq
-- - typos
--
-- Revision 1.2  2003/04/09 13:08:21  ncq
-- - _clinical_ -> _clin_
--
-- Revision 1.1  2003/02/14 10:54:19  ncq
-- - breaking out enumerated data
--
