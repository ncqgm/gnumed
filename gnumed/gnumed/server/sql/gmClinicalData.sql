-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalData.sql,v $
-- $Id: gmClinicalData.sql,v 1.14 2003-10-26 09:41:03 ncq Exp $
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
INSERT INTO _enum_encounter_type (description) values (i18n('in surgery'));
INSERT INTO _enum_encounter_type (description) values (i18n('phone consultation'));
INSERT INTO _enum_encounter_type (description) values (i18n('fax consultation'));
INSERT INTO _enum_encounter_type (description) values (i18n('home visit'));
INSERT INTO _enum_encounter_type (description) values (i18n('nursing home visit'));
INSERT INTO _enum_encounter_type (description) values (i18n('repeat script'));
INSERT INTO _enum_encounter_type (description) values (i18n('hospital visit'));
INSERT INTO _enum_encounter_type (description) values (i18n('video conference'));
INSERT INTO _enum_encounter_type (description) values (i18n('proxy encounter'));
INSERT INTO _enum_encounter_type (description) values (i18n('emergency encounter'));
INSERT INTO _enum_encounter_type (description) values (i18n('other encounter'));

-- ===================================================================
insert into _enum_allergy_type (value) values (i18n('allergy'));
insert into _enum_allergy_type (value) values (i18n('sensitivity'));

-- ===================================================================
INSERT INTO _enum_hx_type (description) values (i18n('past'));
INSERT INTO _enum_hx_type (description) values (i18n('presenting complaint'));
INSERT INTO _enum_hx_type (description) values (i18n('history of present illness'));
INSERT INTO _enum_hx_type (description) values (i18n('social'));
INSERT INTO _enum_hx_type (description) values (i18n('family'));
INSERT INTO _enum_hx_type (description) values (i18n('immunisation'));
INSERT INTO _enum_hx_type (description) values (i18n('requests'));
INSERT INTO _enum_hx_type (description) values (i18n('allergies'));
INSERT INTO _enum_hx_type (description) values (i18n('drug'));
INSERT INTO _enum_hx_type (description) values (i18n('sexual'));
INSERT INTO _enum_hx_type (description) values (i18n('psychiatric'));
INSERT INTO _enum_hx_type (description) values (i18n('other'));

-- ===================================================================
insert into _enum_hx_source (description) values (i18n('patient'));
insert into _enum_hx_source (description) values (i18n('clinician'));
insert into _enum_hx_source (description) values (i18n('relative'));
insert into _enum_hx_source (description) values (i18n('carer'));
insert into _enum_hx_source (description) values (i18n('notes'));
insert into _enum_hx_source (description) values (i18n('correspondence'));

-- ===================================================================
--INSERT INTO enum_coding_systems (description) values (i18n('general'));
--INSERT INTO enum_coding_systems (description) values (i18n('clinical'));
--INSERT INTO enum_coding_systems (description) values (i18n('diagnosis'));
--INSERT INTO enum_coding_systems (description) values (i18n('therapy'));
--INSERT INTO enum_coding_systems (description) values (i18n('pathology'));
--INSERT INTO enum_coding_systems (description) values (i18n('bureaucratic'));
--INSERT INTO enum_coding_systems (description) values (i18n('ean'));
--INSERT INTO enum_coding_systems (description) values (i18n('other'));

-- ===================================================================
INSERT INTO enum_confidentiality_level (description) values (i18n('public'));
INSERT INTO enum_confidentiality_level (description) values (i18n('relatives'));
INSERT INTO enum_confidentiality_level (description) values (i18n('receptionist'));
INSERT INTO enum_confidentiality_level (description) values (i18n('clinical staff'));
INSERT INTO enum_confidentiality_level (description) values (i18n('doctors'));
INSERT INTO enum_confidentiality_level (description) values (i18n('doctors of practice only'));
INSERT INTO enum_confidentiality_level (description) values (i18n('treating doctor'));

-- ===================================================================
insert into drug_units(unit) values('ml');
insert into drug_units(unit) values('mg');
insert into drug_units(unit) values('mg/ml');
insert into drug_units(unit) values('mg/g');
insert into drug_units(unit) values('U');
insert into drug_units(unit) values('IU');
insert into drug_units(unit) values('each');
insert into drug_units(unit) values('mcg');
insert into drug_units(unit) values('mcg/ml');
insert into drug_units(unit) values('IU/ml');
insert into drug_units(unit) values('day');

-- ===================================================================
--I18N!
insert into drug_formulations(description) values ('tablet');
insert into drug_formulations(description) values ('capsule');
insert into drug_formulations(description) values ('syrup');
insert into drug_formulations(description) values ('suspension');
insert into drug_formulations(description) values ('powder');
insert into drug_formulations(description) values ('cream');
insert into drug_formulations(description) values ('ointment');
insert into drug_formulations(description) values ('lotion');
insert into drug_formulations(description) values ('suppository');
insert into drug_formulations(description) values ('solution');
insert into drug_formulations(description) values ('dermal patch');
insert into drug_formulations(description) values ('kit');

-- ===================================================================
--I18N!
insert into drug_routes(description, abbreviation) values('oral', 'o.');
insert into drug_routes(description, abbreviation) values('sublingual', 's.l.');
insert into drug_routes(description, abbreviation) values('nasal', 'nas.');
insert into drug_routes(description, abbreviation) values('topical', 'top.');
insert into drug_routes(description, abbreviation) values('rectal', 'rect.');
insert into drug_routes(description, abbreviation) values('intravenous', 'i.v.');
insert into drug_routes(description, abbreviation) values('intramuscular', 'i.m.');
insert into drug_routes(description, abbreviation) values('subcutaneous', 's.c.');
insert into drug_routes(description, abbreviation) values('intraarterial', 'art.');
insert into drug_routes(description, abbreviation) values('intrathecal', 'i.th.');

-- ===================================================================
insert into enum_immunities (name) values ('tetanus');

-- ===================================================================
-- measurements stuff
-- your own practice as a test-providing org
insert into test_org (id, id_org, comment) values (
	1, -1, 'your own practice'
);

-- measurement definitions
-- weight
insert into test_type (
	id, id_provider, code, coding_system, name, comment, basic_unit
) values (
	1, 1, i18n('wght'), null, i18n('weight (body mass)'), i18n('the patient''s weight (body mass to be accurate)'), 'kg'
);
-- template
insert into test_type (
	id, id_provider, code, coding_system, name, comment, basic_unit
) values (
	2, 1, i18n('hght'), null, i18n('height'), i18n('lying in infants, else standing, see result notes'), 'm'
);
-- blood pressure
-- manually/by device, sitting/lying/standing, Riva-Rocci vs. other methods handled in result specifics
insert into test_type (
	id, id_provider, code, coding_system, name, comment, basic_unit
) values (
	3, 1, i18n('RR'), null, i18n('blood pressure'), i18n('specifics attached to result record'), 'Pa'
);
-- pulse
insert into test_type (
	id, id_provider, code, coding_system, name, comment, basic_unit
) values (
	4, 1, i18n('pulse'), null, i18n('pulse, periph.art.'), i18n('peripheral arterial pulse'), 'Hz'
);
-- peripheral arterial oxygenation
insert into test_type (
	id, id_provider, code, coding_system, name, comment, basic_unit
) values (
	5, 1, i18n('SpO2'), null, i18n('blood oxygen saturation'), i18n('peripheral arterial blood oxygenization level, transduced'), '%'
);
/*
-- template
insert into test_type (
	id, id_provider, code, coding_system, name, comment, basic_unit
) values (
	'missing', 1, i18n(''), null, i18n(''), i18n(''), ''
);
*/
-- ===================================================================
-- vaccination routes
delete from vacc_route;

insert into vacc_route
	(abbreviation, description)
values
	('i.m.', i18n('intramuscular'));

insert into vacc_route
	(abbreviation, description)
values
	('s.c.', i18n('subcutaneous'));

-- ===================================================================
-- vaccination indications
delete from vacc_indication;

insert into vacc_indication (description) values (i18n('measles'));
insert into vacc_indication (description) values (i18n('mumps'));
insert into vacc_indication (description) values (i18n('rubella'));
insert into vacc_indication (description) values (i18n('tetanus'));
insert into vacc_indication (description) values (i18n('diphtheria'));
insert into vacc_indication (description) values (i18n('influenza'));
insert into vacc_indication (description) values (i18n('pneumococcus'));
insert into vacc_indication (description) values (i18n('pertussis'));

-- ===================================================================
-- vaccination indication to disease code links
delete from lnk_vacc_ind2code;

-- ICD 10 GM (German Modification)

-- Measles
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='measles'), 'B05', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='measles'), 'B05.0+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='measles'), 'B05.1+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='measles'), 'B05.2+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='measles'), 'B05.3+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='measles'), 'B05.4+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='measles'), 'B05.8+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='measles'), 'B05.9+', 'ICD-10-GM');

-- Mumps
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='mumps'), 'B26', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='mumps'), 'B26.0+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='mumps'), 'B26.1+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='mumps'), 'B26.2+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='mumps'), 'B26.3+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='mumps'), 'B26.8', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='mumps'), 'B26.9', 'ICD-10-GM');

-- Rubella
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='rubella'), 'B06', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='rubella'), 'B06.0+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='rubella'), 'B06.8', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='rubella'), 'B06.9', 'ICD-10-GM');

-- Tetanus
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='tetanus'), 'A33', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='tetanus'), 'A34', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='tetanus'), 'A35', 'ICD-10-GM');

-- Diptheria
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='diphtheria'), 'A36', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='diphtheria'), 'A36.0', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='diphtheria'), 'A36.1', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='diphtheria'), 'A36.2', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='diphtheria'), 'A36.3', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='diphtheria'), 'A36.8', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='diphtheria'), 'A36.9', 'ICD-10-GM');

-- Influenza
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='influenza'), 'J11', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='influenza'), 'J11.0', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='influenza'), 'J11.1', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='influenza'), 'J11.8', 'ICD-10-GM');

-- Pneumococcus
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pneumococcus'), 'G00.1', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pneumococcus'), 'I30.1', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pneumococcus'), 'M00.1', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pneumococcus'), 'A40.3', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pneumococcus'), 'J13', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pneumococcus'), 'P23.6', 'ICD-10-GM');

-- Pertussis
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pertussis'), 'A37', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pertussis'), 'A37.0', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pertussis'), 'A37.1', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pertussis'), 'A37.8', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	((select id from vacc_indication where description='pertussis'), 'A37.9', 'ICD-10-GM');

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalData.sql,v $', '$Revision: 1.14 $');

-- =============================================
-- $Log: gmClinicalData.sql,v $
-- Revision 1.14  2003-10-26 09:41:03  ncq
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
