-- Projekt GnuMed
-- Impfkalender der Firma Wyeth Lederle für Prevenar (Pneumokokken)

-- Quellen: Beipackzettel

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Impfplan-Prevenar.sql,v $
-- $Revision: 1.1 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
--delete from lnk_vacc_def2regime;
--delete from vacc_def;
--delete from vacc_regime;

----------------------------
-- Kinder unter 6 Monaten --
----------------------------
-- Impfplan erstellen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='pneumococcus'),
	'Pneumokokken (<6 Monate, Hersteller)'
);

-- Impfzeitpunkte definieren
insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	1,
	'2 months'::interval,
	'6 months'::interval,
	false,
	'1 month'::interval,
	'<6 Monate, Hersteller'
);

insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	2,
	'3 months'::interval,
	'7 months'::interval,
	false,
	'1 month'::interval,
	'<6 Monate, Hersteller'
);

insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	3,
	'4 months'::interval,
	'8 months'::interval,
	false,
	'1 month'::interval,
	'<6 Monate, Hersteller'
);

insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	4,
	'1 year'::interval,
	'2 years'::interval,
	false,
	'8 months'::interval,
	'<6 Monate, Hersteller'
);

-- und in Impfplan eintragen
insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 2)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 3)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 4)
);

--------------------------------------
-- Kinder zwischen 7 und 11 Monaten --
--------------------------------------
-- Impfplan erstellen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='pneumococcus'),
	'Pneumokokken (7-11 Monate, Hersteller)'
);

-- Impfzeitpunkte definieren
insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	1,
	'7 months'::interval,
	'11 months'::interval,
	false,
	'1 month'::interval,
	'7-11 Monate, Hersteller'
);

insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	2,
	'8 months'::interval,
	'12 months'::interval,
	false,
	'1 month'::interval,
	'7-11 Monate, Hersteller'
);

insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	3,
	'1 year'::interval,
	'2 years'::interval,
	false,
	'1 month'::interval,
	'7-11 Monate, Hersteller'
);

-- und in Impfplan eintragen
insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 2)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 3)
);

---------------------------------------
-- Kinder zwischen 12 und 23 Monaten --
---------------------------------------
-- Impfplan erstellen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	(select id from vacc_indication where description='pneumococcus'),
	'Pneumokokken (12-23 Monate, Hersteller)'
);

-- Impfzeitpunkte definieren
insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	1,
	'12 months'::interval,
	'23 months'::interval,
	false,
	'2 month'::interval,
	'12-23 Monate, Hersteller'
);

insert into vacc_def
	(fk_indication, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	(select id from vacc_indication where description='pneumococcus'),
	2,
	'14 months'::interval,
	'25 months'::interval,
	false,
	'2 month'::interval,
	'12-23 Monate, Hersteller'
);

-- und in Impfplan eintragen
insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select id from vacc_indication where description='pneumococcus') and seq_no = 2)
);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename like '%Impfkalender-Prevenar%';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: Impfplan-Prevenar.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: Impfplan-Prevenar.sql,v $
-- Revision 1.1  2003-11-26 00:10:45  ncq
-- - Prevenar
--
