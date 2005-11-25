-- Projekt GnuMed
-- Impfkalender der STIKO (Deutschland)

-- Quellen:
-- Kinderärztliche Praxis (2002)
-- Sonderheft "Impfen 2002"
-- Kirchheim-Verlag Mainz

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/STIKO-Impfkalender.sql,v $
-- $Revision: 1.17 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- FIXME: we currently assume that the services [reference]
-- and [historica] reside in the same database (see fk_recommended_by)

-- STIKO
delete from ref_source where name_short = 'STIKO';
insert into ref_source (
	name_short,
	name_long,
	version,
	description,
	source
) values (
	'STIKO',
	'Ständige Impfkommission, Robert-Koch-Institut',
	'Juli 2002',
	'Standardimpfungen für Säuglinge, Kinder, Jugendliche und Erwachsene',
	'"Kinderärztliche Praxis" (2002), Sonderheft "Impfen 2002", Kirchheim-Verlag Mainz'
);

delete from clin.vacc_def;
delete from clin.vacc_regime where name like '%STIKO%';

------------
-- Masern --
------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='measles'),
	'Masern (STIKO)'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vacc_regime_id_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vacc_regime_id_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

-----------
-- Mumps --
-----------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='mumps'),
	'Mumps (STIKO)'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vacc_regime_id_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vacc_regime_id_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

------------
-- Röteln --
------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='rubella'),
	'Röteln (STIKO)'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vacc_regime_id_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vacc_regime_id_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

-------------
-- Tetanus --
-------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='tetanus'),
	'Tetanus (STIKO)'
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
	'nach 10 Jahren falls keine Verletzung, nach 7 Jahren bei kleinen Verletzungen, bei großen Verletzungen nach 5 Jahren'
);

----------------
-- Diphtherie --
----------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='diphtheria'),
	'Diphtherie (STIKO)'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values
	(currval('clin.vacc_regime_id_seq'), 1, '2 months'::interval, '2 months'::interval);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vacc_regime_id_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

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
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vacc_regime_id_seq'),
	6,
	'9 years'::interval,
	'17 years'::interval,
	'4 weeks'::interval,
	'Impfstoff mit reduziertem Toxoidgehalt (d) verwenden !'
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('clin.vacc_regime_id_seq'),
	null,
	'5 years'::interval,
	'10 years'::interval,
	true,
	'10 years'::interval,
	'Impfstoff mit reduziertem Toxoidgehalt (d) verwenden !'
);

---------------
-- Pertussis --
---------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='pertussis'),
	'Pertussis (STIKO)'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values
	(currval('clin.vacc_regime_id_seq'), 1, '2 months'::interval, '2 months'::interval);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vacc_regime_id_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

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
values (
	currval('clin.vacc_regime_id_seq'),
	5,
	'9 years'::interval,
	'17 years'::interval,
	'5 years'::interval
);

---------
-- HiB --
---------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='haemophilus influenzae b'),
	'HiB (STIKO)',
	'falls Mehrfachimpfstoff mit Pertussis (aP), dann Schema wie DTaP/Dt/Td anwenden'
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

----------
-- HepB --
----------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='hepatitis B'),
	'HepB (STIKO)',
	'falls Mehrfachimpfstoff mit Pertussis (aP), dann Schema wie DTaP/Dt/Td anwenden,
	 fehlende Grundimmunisierung/Komplettierung zwischen 9 und 17 Jahren'
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

-----------
-- Polio --
-----------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='poliomyelitis'),
	'Polio (STIKO)',
	'falls Mehrfachimpfstoff mit Pertussis (aP), dann Schema wie DTaP/Dt/Td anwenden'
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

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vacc_regime_id_seq'),
	4,
	'9 years'::interval,
	'17 years'::interval,
	'5 years'::interval
);

---------------
-- Influenza --
---------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='influenza'),
	'Influenza (STIKO)'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, is_booster, min_interval, comment)
values (
	currval('clin.vacc_regime_id_seq'),
	null,
	'18 years'::interval,
	true,
	'1 year'::interval,
	'jährlich neu von WHO empfohlener Impfstoff'
);

------------------
-- Pneumokokken --
------------------
-- Impfplan definieren (STIKO)
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='pneumococcus'),
	'Pneumokokken (STIKO)',
	'ab 18 Jahre'
);

-- Impfzeitpunkte (STIKO) festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, is_booster, min_interval, comment)
values (
	currval('clin.vacc_regime_id_seq'),
	null,
	'18 years'::interval,
	true,
	'6 years'::interval,
	'Polysaccharid-Impfstoff'
);

---------------------
-- Meningokokken C --
---------------------
-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='meningococcus C'),
	'MenC-Infant (STIKO)',
	'2-12 Monate, Meningokokken C'
);

-- Impfzeitpunkte festlegen
insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vacc_regime_id_seq'),
	1,
	'2 months'::interval,
	'12 months'::interval
);

insert into clin.vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vacc_regime_id_seq'),
	2,
	'4 months'::interval,
	'14 months'::interval,
	'2 months'::interval
);

-- Impfplan definieren
insert into clin.vacc_regime
	(fk_recommended_by, fk_indication, name, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='meningococcus C'),
	'MenC (STIKO)',
	'ab 12 Monaten, Meningokokken C'
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
-- do simple revision tracking
delete from gm_schema_revision where filename='$RCSfile: STIKO-Impfkalender.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: STIKO-Impfkalender.sql,v $', '$Revision: 1.17 $');

-- =============================================
-- $Log: STIKO-Impfkalender.sql,v $
-- Revision 1.17  2005-11-25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.16  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.15  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.14  2004/10/12 11:23:31  ncq
-- - fix Polio regime being wrongly linked to HepB indication
--
-- Revision 1.13  2004/04/14 20:03:59  ncq
-- - fix check constraints on intervals
--
-- Revision 1.12  2004/04/14 13:33:04  ncq
-- - need to adjust min_interval for seq_no=1 after tightening interval checks
--
-- Revision 1.11  2004/03/18 09:58:50  ncq
-- - removed is_booster reference where is false
--
-- Revision 1.10  2003/12/29 16:01:21  uid66147
-- - use lnk_vacc2vacc_def
-- - add STIKO gmReference entry
-- - more appropriate vacc_regime.name values
-- - add HiB/HepB
--
-- Revision 1.9  2003/12/03 19:09:46  ncq
-- - NeisVac-C
--
-- Revision 1.8  2003/12/01 23:53:18  ncq
-- - delete more selectively
--
-- Revision 1.7  2003/12/01 22:22:41  ncq
-- - vastly improve strings
--
-- Revision 1.6  2003/11/26 23:19:08  ncq
-- - vacc_def now links to vacc_regime instead of vacc_indication
--
-- Revision 1.5  2003/10/31 23:30:28  ncq
-- - cleanup
--
-- Revision 1.4  2003/10/26 09:41:03  ncq
-- - truncate -> delete from
--
-- Revision 1.3  2003/10/25 16:45:19  ncq
-- - seq_id -> seq_no
--
-- Revision 1.2  2003/10/21 15:04:49  ncq
-- - update vaccination schedules for Germany
--
-- Revision 1.1  2003/10/19 15:17:41  ncq
-- - German vaccination regimes recommended by the STIKO
--
