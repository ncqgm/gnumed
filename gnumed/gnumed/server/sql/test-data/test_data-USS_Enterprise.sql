-- Projekt GnuMed
-- USS Enterprise defs

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-USS_Enterprise.sql,v $
-- $Revision: 1.13 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1


-- =============================================
-- vaccination related data

---------------------
-- Tetanus vaccine --
---------------------
insert into vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from vacc_route where abbreviation='i.m.'),
	'Tetasorbat (SFCMS)',
	'Tetanus',
	false,
	-- FIXME: check this
	'1 year'::interval,
	'Starfleet Central Medical Supplies'
);

-- link to indications
insert into lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('vaccine_id_seq'), (select id from vacc_indication where description='tetanus'));


-- FIXME: we currently assume that the services [reference]
-- and [historica] reside in the same database (see fk_recommended_by)

-- Enterprise Vaccination Council
delete from ref_source where name_short = 'SFCVC';
insert into ref_source (
	name_short,
	name_long,
	version,
	description,
	source
) values (
	'SFCVC',
	'Starfleet Central Vaccination Council',
	'December 2004',
	'vaccination recommendations for Starfleet personnel',
	'Starfleet Central Medical Facilities, Earth'
);

delete from vacc_regime where fk_recommended_by = currval('ref_source_pk_seq');

-------------
-- Tetanus --
-------------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	currval('ref_source_pk_seq'),
	(select id from vacc_indication where description='tetanus'),
	'Tetanus (SFCVC)'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('vacc_regime_id_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	2,
	'3 months'::interval,
	'3 months'::interval,
	'4 weeks'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_regime_id_seq'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_regime_id_seq'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_regime_id_seq'), 5, '4 years'::interval, '5 years'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_regime_id_seq'), 6, '9 years'::interval, '17 years'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	null,
	'5 years'::interval,
	'10 years'::interval,
	true,
	'10 years'::interval,
	'at +10 years if no injury, at +7 years if minor injury, at +5 years if major injury,
	 however, US military studies show adequate titers w/o boosters at +30 years'
);

---------
-- HiB --
---------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from vacc_indication where description='haemophilus influenzae b'),
	'HiB (SFCVC)',
	'if combined w/ pertussis vaccine (aP) use DTaP/Dt/Td regime'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('vacc_regime_id_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	2,
	'4 months'::interval,
	'4 months'::interval,
	'4 weeks'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	3,
	'11 months'::interval,
	'14 months'::interval,
	'4 weeks'::interval
);

---------------------
-- Meningokokken C --
---------------------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from vacc_indication where description='meningococcus C'),
	'MenC (SFCVC)',
	'> 12 months of age, meningococcus C'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due)
values (
	currval('vacc_regime_id_seq'),
	1,
	'12 months'::interval
);


-- =============================================
-- pathology lab
insert into test_org
	(fk_org, fk_adm_contact, fk_med_contact, internal_name, comment)
values (
	99999,
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='Spock' and dob='1931-3-26+2:00'::timestamp),
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20+2:00'::timestamp),
	'Enterprise Main Lab',
	'the main path lab aboard the USS Enterprise'
);

-- FIXME: delete statements

-- tests
-- WBC
insert into test_type
	(fk_test_org, code, name, comment, conversion_unit)
values (
	currval('test_org_pk_seq'),
	'WBC-EML',
	'leukocytes (EML)',
	'EDTA sample',
	'Gpt/l'
);

insert into test_type_local (code, name)
values (
	'WBC',
	'leukocytes'
);

insert into lnk_ttype2local_type (fk_test_type, fk_test_type_local)
values (
	currval('test_type_pk_seq'),
	currval('test_type_local_pk_seq')
);

-- RBC
insert into test_type
	(fk_test_org, code, name, comment, conversion_unit)
values (
	currval('test_org_pk_seq'),
	'RBC-EML',
	'erythrocytes (EML)',
	'EDTA sample',
	'Tpt/l'
);

insert into test_type_local (code, name)
values (
	'RBC',
	'erythrocytes'
);

insert into lnk_ttype2local_type (fk_test_type, fk_test_type_local)
values (
	currval('test_type_pk_seq'),
	currval('test_type_local_pk_seq')
);

-- PLT
insert into test_type
	(fk_test_org, code, name, comment, conversion_unit)
values (
	currval('test_org_pk_seq'),
	'PLT-EML',
	'platelets (EML)',
	'EDTA sample',
	'Gpt/l'
);

insert into test_type_local (code, name)
values (
	'PLT',
	'platelets'
);

insert into lnk_ttype2local_type (fk_test_type, fk_test_type_local)
values (
	currval('test_type_pk_seq'),
	currval('test_type_local_pk_seq')
);

-- CRP
insert into test_type
	(fk_test_org, code, name, comment, conversion_unit)
values (
	currval('test_org_pk_seq'),
	'CRP-EML',
	'C-reactive protein (EML)',
	'blood serum',
	'mg/l'
);

insert into test_type_local (code, name)
values (
	'CRP',
	'C-reactive protein'
);

insert into lnk_ttype2local_type (fk_test_type, fk_test_type_local)
values (
	currval('test_type_pk_seq'),
	currval('test_type_local_pk_seq')
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-USS_Enterprise.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-USS_Enterprise.sql,v $', '$Revision: 1.13 $');

-- =============================================
-- $Log: test_data-USS_Enterprise.sql,v $
-- Revision 1.13  2004-12-18 10:05:36  ncq
-- - id -> pk
--
-- Revision 1.12  2004/12/18 09:57:17  ncq
-- - add vaccination related data
--
-- Revision 1.11  2004/09/29 19:16:28  ncq
-- - fix test type defs
--
-- Revision 1.10  2004/09/29 10:31:11  ncq
-- - test_type.id -> pk
-- - basic_unit -> conversion_unit
--
-- Revision 1.9  2004/06/02 14:41:18  ncq
-- - remove offending set time zone statement
--
-- Revision 1.8  2004/06/02 13:46:46  ncq
-- - setting default session timezone has incompatible syntax
--   across version range 7.1-7.4, henceforth specify timezone
--   directly in timestamp values, which works
--
-- Revision 1.7  2004/06/02 00:14:47  ncq
-- - add time zone setting
--
-- Revision 1.6  2004/05/06 23:32:44  ncq
-- - internal_name now local_name
-- - technically_abnormal now text
--
-- Revision 1.5  2004/03/23 17:34:50  ncq
-- - support and use optionally cross-provider unified test names
--
-- Revision 1.4  2004/03/19 11:56:59  ncq
-- - remove misleading URL
--
-- Revision 1.3  2004/03/18 18:32:09  ncq
-- - thrombocytes -> platelets
--
-- Revision 1.2  2004/03/18 10:29:51  ncq
-- - set fk_org on EML to 99999
--
-- Revision 1.1  2004/03/18 10:22:25  ncq
-- - Enterprise path lab
--
