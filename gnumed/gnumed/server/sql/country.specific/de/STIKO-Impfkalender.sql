-- Projekt GnuMed
-- Impfkalender der STIKO (Deutschland)

-- Quellen:
-- Kinderärztliche Praxis (2002)
-- Sonderheft "Impfen 2002"
-- Kirchheim-Verlag Mainz

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/STIKO-Impfkalender.sql,v $
-- $Revision: 1.6 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
delete from vacc_def;
delete from vacc_regime;

------------
-- Masern --
------------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='measles'),
	'Masern-Impfung, meist in MMR-Kombination'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval,
	'4 weeks'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

-----------
-- Mumps --
-----------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='mumps'),
	'Mumps-Impfung, meist in MMR-Kombination'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval,
	'4 weeks'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

------------
-- Röteln --
------------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='rubella'),
	'Röteln-Impfung, meist in MMR-Kombination'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval,
	'4 weeks'::interval
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

-------------
-- Tetanus --
-------------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='tetanus'),
	'Tetanus-Impfung, meist in DTaP- bzw. DT/Td-Kombination'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('vacc_regime_id_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval,
	'4 weeks'::interval
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
	-1,
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
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='diphtheria'),
	'Diphtherie-Impfung, meist in DTaP- bzw. DT/Td-Kombination'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_regime_id_seq'), 1, '2 months'::interval, '2 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_regime_id_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

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
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	6,
	'9 years'::interval,
	'17 years'::interval,
	'4 weeks'::interval,
	'Impfstoff mit reduziertem Toxoidgehalt (d) verwenden !'
);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	-1,
	'5 years'::interval,
	'10 years'::interval,
	true,
	'10 years'::interval,
	'Impfstoff mit reduziertem Toxoidgehalt (d) verwenden !'
);

---------------
-- Influenza --
---------------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='influenza'),
	'jährlich neu von WHO empfohlener Impfstoff'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	-1,
	'18 years'::interval,
	'-1'::interval,
	true,
	'1 year'::interval,
	'jährlich neu von WHO empfohlener Impfstoff'
);

------------------
-- Pneumokokken --
------------------
-- Impfplan definieren (STIKO)
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='pneumococcus'),
	'Pneumokokken (ab 18, STIKO)'
);

-- Impfzeitpunkte (STIKO) festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('vacc_regime_id_seq'),
	-1,
	'18 years'::interval,
	'-1'::interval,
	true,
	'6 years'::interval,
	'Polysaccharid-Impfstoff'
);

---------------
-- Pertussis --
---------------
-- Impfplan definieren
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='pertussis'),
	'Pertussis-Impfung, oft in DTaP-Kombination'
);

-- Impfzeitpunkte festlegen
insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_regime_id_seq'), 1, '2 months'::interval, '2 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_regime, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_regime_id_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

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
	(currval('vacc_regime_id_seq'),	5, '9 years'::interval,	'17 years'::interval, '4 weeks'::interval);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename like '%STIKO-Impfkalender%';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: STIKO-Impfkalender.sql,v $', '$Revision: 1.6 $');

-- =============================================
-- $Log: STIKO-Impfkalender.sql,v $
-- Revision 1.6  2003-11-26 23:19:08  ncq
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
