-- Projekt GnuMed
-- Impfkalender der STIKO (Deutschland)

-- Quelle:
-- Kinderärztliche Praxis (2002)
-- Sonderheft "Impfen 2002"
-- Kirchheim-Verlag Mainz

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/STIKO-Impfkalender.sql,v $
-- $Revision: 1.1 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

truncate vacc_indication;
truncate lnk_vacc_ind2code;
truncate vacc_def;
truncate vacc_regime;
truncate lnk_vacc_def2regime;

------------
-- Masern --
------------
-- Impfindikation
insert into vacc_indication (description) values ('Masern');

-- ICD-10 links
insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	(currval('vacc_indication_id_seq'), 'B05', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	(currval('vacc_indication_id_seq'), 'B05.0+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	(currval('vacc_indication_id_seq'), 'B05.1+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	(currval('vacc_indication_id_seq'), 'B05.2+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	(currval('vacc_indication_id_seq'), 'B05.3+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	(currval('vacc_indication_id_seq'), 'B05.4+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	(currval('vacc_indication_id_seq'), 'B05.8+', 'ICD-10-GM');

insert into lnk_vacc_ind2code
	(fk_indication, code, coding_system)
values
	(currval('vacc_indication_id_seq'), 'B05.9+', 'ICD-10-GM');

-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 1, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 2, '15 months'::interval, '23 months'::interval, '4 weeks'::interval);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	currval('vacc_indication_id_seq'),
	'Masern-Impfung, meist in MMR-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 2)
);

-----------
-- Mumps --
-----------
-- Impfindikation
insert into vacc_indication (description) values ('Mumps');

-- ICD-10 links
--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.0+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.1+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.2+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.3+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.4+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.8+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.9+', 'ICD-10-GM');

-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 1, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 2, '15 months'::interval, '23 months'::interval, '4 weeks'::interval);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	currval('vacc_indication_id_seq'),
	'Mumps-Impfung, meist in MMR-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 2)
);

------------
-- Röteln --
------------
-- Impfindikation
insert into vacc_indication (description) values ('Röteln');

-- ICD-10 links
--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.0+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.1+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.2+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.3+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.4+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.8+', 'ICD-10-GM');

--insert into lnk_vacc_ind2code
--	(fk_indication, code, coding_system)
--values
--	(currval('vacc_indication_id_seq'), 'B05.9+', 'ICD-10-GM');

-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 1, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 2, '15 months'::interval, '23 months'::interval, '4 weeks'::interval);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	currval('vacc_indication_id_seq'),
	'Röteln-Impfung, meist in MMR-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 2)
);

-------------
-- Tetanus --
-------------
-- Impfindikation
insert into vacc_indication (description) values ('Tetanus');

-- ICD-10 links

-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 1, '2 months'::interval, '2 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 5, '4 years'::interval, '5 years'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 6, '9 years'::interval, '17 years'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('vacc_indication_id_seq'),
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
	currval('vacc_indication_id_seq'),
	'Tetanus-Impfung, meist in DTaP- bzw. DT/Td-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 2)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 3)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 4)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 5)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 6)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and is_booster = true)
);

----------------
-- Diphtherie --
----------------
-- Impfindikation
insert into vacc_indication (description) values ('Diphtherie');

-- ICD-10 links

-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 1, '2 months'::interval, '2 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 5, '4 years'::interval, '5 years'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval, comment)
values (
	currval('vacc_indication_id_seq'),
	6,
	'9 years'::interval,
	'17 years'::interval,
	'4 weeks'::interval,
	'Impfstoff mit reduziertem Toxoidgehalt (d) verwenden !'
);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('vacc_indication_id_seq'),
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
	currval('vacc_indication_id_seq'),
	'Diphtherie-Impfung, meist in DTaP- bzw. DT/Td-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 2)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 3)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 4)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 5)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 6)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and is_booster = true)
);

---------------
-- Influenza --
---------------
-- Impfindikation
insert into vacc_indication (description) values ('Influenza');

-- ICD-10 links

-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('vacc_indication_id_seq'),
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
	currval('vacc_indication_id_seq'),
	'jährlich neu von WHO empfohlener Impfstoff'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and is_booster = true)
);

------------------
-- Pneumokokken --
------------------
-- Impfindikation
insert into vacc_indication (description) values ('Pneumokokken');

-- ICD-10 links

-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('vacc_indication_id_seq'),
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
	currval('vacc_indication_id_seq'),
	'Polysaccharid-Impfstoff'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and is_booster = true)
);

---------------
-- Pertussis --
---------------
-- Impfindikation
insert into vacc_indication (description) values ('Pertussis');

-- ICD-10 links

-- Impfstoffe

-- Impfzeitpunkte
insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 1, '2 months'::interval, '2 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into vacc_def
	(fk_indication, seq_id, min_age_due, max_age_due, min_interval)
values
	(currval('vacc_indication_id_seq'),	5, '9 years'::interval,	'17 years'::interval, '4 weeks'::interval);

-- in Impfplan eintragen
insert into vacc_regime
	(fk_recommended_by, fk_indication, description)
values (
	1,
	currval('vacc_indication_id_seq'),
	'Pertussis-Impfung, oft in DTaP-Kombination'
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 1)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 2)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 3)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 4)
);

insert into lnk_vacc_def2regime
	(fk_regime, fk_vacc_def)
values (
	currval('vacc_regime_id_seq'),
	(select id from vacc_def where fk_indication = (select currval('vacc_indication_id_seq')) and seq_id = 5)
);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename like '%STIKO%';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: STIKO-Impfkalender.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: STIKO-Impfkalender.sql,v $
-- Revision 1.1  2003-10-19 15:17:41  ncq
-- - German vaccination regimes recommended by the STIKO
--
