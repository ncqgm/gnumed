-- Projekt GnuMed
-- Impfkalender der STIKO (Deutschland)

-- Quellen:
-- Kinderärztliche Praxis (2002)
-- Sonderheft "Impfen 2002"
-- Kirchheim-Verlag Mainz
--
-- ICD-10-GM

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/STIKO-Impfkalender.sql,v $
-- $Revision: 1.2 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
truncate vacc_def;
truncate vacc_regime;
truncate lnk_vacc_def2regime;

------------
-- Masern --
------------
-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='measles'), 1, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='measles'), 2, '15 months'::interval, '23 months'::interval, '4 weeks'::interval);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='measles'),
	'Masern-Impfung, meist in MMR-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='measles') and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='measles') and seq_id = 2)
);

-----------
-- Mumps --
-----------
-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='mumps'), 1, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='mumps'), 2, '15 months'::interval, '23 months'::interval, '4 weeks'::interval);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='mumps'),
	'Mumps-Impfung, meist in MMR-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='mumps') and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='mumps') and seq_id = 2)
);

------------
-- Röteln --
------------
-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='rubella'), 1, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='rubella'), 2, '15 months'::interval, '23 months'::interval, '4 weeks'::interval);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='rubella'),
	'Röteln-Impfung, meist in MMR-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='rubella') and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='rubella') and seq_id = 2)
);

-------------
-- Tetanus --
-------------
-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='tetanus'), 1, '2 months'::interval, '2 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='tetanus'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='tetanus'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='tetanus'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='tetanus'), 5, '4 years'::interval, '5 years'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='tetanus'), 6, '9 years'::interval, '17 years'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='tetanus'),
	-1,
	'5 years'::interval,
	'10 years'::interval,
	true,
	'10 years'::interval,
	'nach 10 Jahren falls keine Verletzung, nach 7 Jahren bei kleinen Verletzungen, bei großen Verletzungen nach 5 Jahren'
);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='tetanus'),
	'Tetanus-Impfung, meist in DTaP- bzw. DT/Td-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='tetanus') and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='tetanus') and seq_id = 2)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='tetanus') and seq_id = 3)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='tetanus') and seq_id = 4)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='tetanus') and seq_id = 5)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='tetanus') and seq_id = 6)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='tetanus') and is_booster = true)
);

----------------
-- Diphtherie --
----------------
-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='diphtheria'), 1, '2 months'::interval, '2 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='diphtheria'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='diphtheria'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='diphtheria'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='diphtheria'), 5, '4 years'::interval, '5 years'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval, comment)
values (
	(select id from vacc_indication where description='diphtheria'),
	6,
	'9 years'::interval,
	'17 years'::interval,
	'4 weeks'::interval,
	'Impfstoff mit reduziertem Toxoidgehalt (d) verwenden !'
);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='diphtheria'),
	-1,
	'5 years'::interval,
	'10 years'::interval,
	true,
	'10 years'::interval,
	'Impfstoff mit reduziertem Toxoidgehalt (d) verwenden !'
);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='diphtheria'),
	'Diphtherie-Impfung, meist in DTaP- bzw. DT/Td-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='diphtheria') and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='diphtheria') and seq_id = 2)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='diphtheria') and seq_id = 3)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='diphtheria') and seq_id = 4)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='diphtheria') and seq_id = 5)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='diphtheria') and seq_id = 6)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='diphtheria') and is_booster = true)
);

---------------
-- Influenza --
---------------
-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='influenza'),
	-1,
	'18 years'::interval,
	'-1'::interval,
	true,
	'1 year'::interval,
	'jährlich neu von WHO empfohlener Impfstoff'
);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='influenza'),
	'jährlich neu von WHO empfohlener Impfstoff'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='influenza') and is_booster = true)
);

------------------
-- Pneumokokken --
------------------
-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	-1,
	'18 years'::interval,
	'-1'::interval,
	true,
	'6 years'::interval,
	'Polysaccharid-Impfstoff'
);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='pneumococcus'),
	'Polysaccharid-Impfstoff'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and is_booster = true)
);

---------------
-- Pertussis --
---------------
-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='pertussis'), 1, '2 months'::interval, '2 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='pertussis'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='pertussis'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='pertussis'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	((select id from vacc_indication where description='pertussis'),	5, '9 years'::interval,	'17 years'::interval, '4 weeks'::interval);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='pertussis'),
	'Pertussis-Impfung, oft in DTaP-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pertussis') and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pertussis') and seq_id = 2)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pertussis') and seq_id = 3)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pertussis') and seq_id = 4)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pertussis') and seq_id = 5)
);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename like '%STIKO-Impfkalender%';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: STIKO-Impfkalender.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: STIKO-Impfkalender.sql,v $
-- Revision 1.2  2003-10-21 15:04:49  ncq
-- - update vaccination schedules for Germany
--
-- Revision 1.1  2003/10/19 15:17:41  ncq
-- - German vaccination regimes recommended by the STIKO
--
