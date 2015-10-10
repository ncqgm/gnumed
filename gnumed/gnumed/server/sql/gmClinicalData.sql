-- Project: GNUmed
-- ===================================================================
-- license: GPL v2 or later
-- author: Ian Haywood, Horst Herb

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

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

select i18n.i18n(' (closed)');

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
-- and a link to spouses name, type of work, ethnicity
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalData.sql,v $', '$Revision: 1.46 $');
