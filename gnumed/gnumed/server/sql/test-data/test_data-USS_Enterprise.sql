-- Project GNUmed
-- USS Enterprise defs

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-USS_Enterprise.sql,v $
-- $Revision: 1.24 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
delete from cfg.db_logon_banner;
insert into cfg.db_logon_banner (message) values (
i18n.i18n('Welcome to the USS Enterprise Medical Department GNUmed database.

This database is the default installation intended for demonstration of the GNUmed client. It may be running on a publicly accessible server on the internet. Therefore any data you enter here is likely to be lost when the database is upgraded. It is also put at risk of unlawful disclosure.

DO NOT USE THIS DATABASE TO STORE REAL LIVE PATIENT DATA.


Starfleet Central Medical Facilities')
);

-- =============================================
-- vaccination related data

delete from clin.vaccine where comment = 'Starfleet Central Medical Supplies';
---------------------
-- Tetanus vaccine --
---------------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Tetasorbat (SFCMS)',
	'Tetanus',
	false,
	'1 year'::interval,
	'Starfleet Central Medical Supplies'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tetanus'));


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

delete from clin.vacc_regime where fk_recommended_by = (select pk from ref_source where name_short='SFCVC');

-------------
-- Tetanus --
-------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	(select pk from ref_source where name_short='SFCVC'),
	(select id from clin.vacc_indication where description='tetanus'),
	'Tetanus (SFCVC)'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vacc_regime_id_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vacc_regime_id_seq'),
	2,
	'3 months'::interval,
	'3 months'::interval,
	'4 weeks'::interval
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vacc_regime_id_seq'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vacc_regime_id_seq'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vacc_regime_id_seq'), 5, '4 years'::interval, '5 years'::interval, '4 weeks'::interval);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vacc_regime_id_seq'), 6, '9 years'::interval, '17 years'::interval, '4 weeks'::interval);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('clin.vacc_regime_id_seq'),
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
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	(select pk from ref_source where name_short='SFCVC'),
	(select id from clin.vacc_indication where description='haemophilus influenzae b'),
	'HiB (SFCVC)',
	'if combined w/ pertussis vaccine (aP) use DTaP/Dt/Td regime'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vacc_regime_id_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vacc_regime_id_seq'),
	2,
	'4 months'::interval,
	'4 months'::interval,
	'4 weeks'::interval
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vacc_regime_id_seq'),
	3,
	'11 months'::interval,
	'14 months'::interval,
	'4 weeks'::interval
);

---------------------
-- Meningokokken C --
---------------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	(select pk from ref_source where name_short='SFCVC'),
	(select id from clin.vacc_indication where description='meningococcus C'),
	'MenC (SFCVC)',
	'> 12 months of age, meningococcus C'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due)
values (
	currval('clin.vacc_regime_id_seq'),
	1,
	'12 months'::interval
);


-- =============================================
-- pathology lab
insert into clin.test_org
	(fk_org, fk_adm_contact, fk_med_contact, internal_name, comment)
values (
	99999,
	(select pk_identity from dem.v_basic_person where lastnames='Spock' and dob='1931-3-26+2:00'::timestamp),
	(select pk_identity from dem.v_basic_person where firstnames='Leonard Horatio' and lastnames='McCoy' and dob='1920-1-20+2:00'::timestamp),
	'Enterprise Main Lab',
	'the main path lab aboard the USS Enterprise'
);

-- FIXME: delete statements

-- tests
-- WBC
insert into clin.test_type
	(fk_test_org, code, name, comment, conversion_unit)
values (
	currval('clin.test_org_pk_seq'),
	'WBC-EML',
	'leukocytes (EML)',
	'EDTA sample',
	'Gpt/l'
);

insert into clin.test_type_unified (code, name)
values (
	'WBC',
	'leukocytes'
);

insert into clin.lnk_ttype2unified_type (fk_test_type, fk_test_type_unified)
values (
	currval('clin.test_type_pk_seq'),
	currval('clin.test_type_unified_pk_seq')
);

-- RBC
insert into clin.test_type
	(fk_test_org, code, name, comment, conversion_unit)
values (
	currval('clin.test_org_pk_seq'),
	'RBC-EML',
	'erythrocytes (EML)',
	'EDTA sample',
	'Tpt/l'
);

insert into clin.test_type_unified (code, name)
values (
	'RBC',
	'erythrocytes'
);

insert into clin.lnk_ttype2unified_type (fk_test_type, fk_test_type_unified)
values (
	currval('clin.test_type_pk_seq'),
	currval('clin.test_type_unified_pk_seq')
);

-- PLT
insert into clin.test_type
	(fk_test_org, code, name, comment, conversion_unit)
values (
	currval('clin.test_org_pk_seq'),
	'PLT-EML',
	'platelets (EML)',
	'EDTA sample',
	'Gpt/l'
);

insert into clin.test_type_unified (code, name)
values (
	'PLT',
	'platelets'
);

insert into clin.lnk_ttype2unified_type (fk_test_type, fk_test_type_unified)
values (
	currval('clin.test_type_pk_seq'),
	currval('clin.test_type_unified_pk_seq')
);

-- CRP
insert into clin.test_type
	(fk_test_org, code, name, comment, conversion_unit)
values (
	currval('clin.test_org_pk_seq'),
	'CRP-EML',
	'C-reactive protein (EML)',
	'blood serum',
	'mg/l'
);

insert into clin.test_type_unified (code, name)
values (
	'CRP',
	'C-reactive protein'
);

insert into clin.lnk_ttype2unified_type (fk_test_type, fk_test_type_unified)
values (
	currval('clin.test_type_pk_seq'),
	currval('clin.test_type_unified_pk_seq')
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-USS_Enterprise.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-USS_Enterprise.sql,v $', '$Revision: 1.24 $');

-- =============================================
-- $Log: test_data-USS_Enterprise.sql,v $
-- Revision 1.24  2006-01-18 23:09:48  ncq
-- - improve, spell-fix and translate database logon banner
--
-- Revision 1.23  2006/01/06 10:12:03  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.22  2005/12/29 21:48:09  ncq
-- - clin.vaccine.id -> pk
-- - remove clin.vaccine.last_batch_no
-- - add clin.vaccine_batches
-- - adjust test data and country data
--
-- Revision 1.21  2005/12/27 19:13:59  ncq
-- - add database logon banner
--
-- Revision 1.20  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.19  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.18  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.17  2005/02/13 15:08:23  ncq
-- - add names of actors and some comments
--
-- Revision 1.16  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.15  2005/02/07 13:10:54  ncq
-- - some lab tables changed so we need to keep up with that
--
-- Revision 1.14  2004/12/18 10:13:03  ncq
-- - cleanup
--
-- Revision 1.13  2004/12/18 10:05:36  ncq
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
