-- Projekt GNUmed
-- Impfkalender der STIKO (Deutschland)

-- Quellen:
-- Kinderärztliche Praxis (2002)
-- Sonderheft "Impfen 2002"
-- Kirchheim-Verlag Mainz

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
delete from clin.vaccination_schedule where name like '%(STIKO)%';
delete from clin.vaccination_course where fk_recommended_by = (select pk from ref_source where name_short='STIKO');

-- FIXME: we currently assume that the services [reference]
-- and [historica] reside in the same database (see fk_recommended_by)
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

------------
-- Masern --
------------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='measles')
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

-----------
-- Mumps --
-----------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='mumps')
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

------------
-- Röteln --
------------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='rubella')
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'11 months'::interval,
	'14 months'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'15 months'::interval,
	'23 months'::interval,
	'4 weeks'::interval
);

------------------
-- MMR-Schedule --
------------------
insert into clin.vaccination_schedule (name, comment) values (
	'MMR (STIKO)',
	'Mindestabstand zwischen 2 Impfungen: 4 Wochen'
);

-- Masern
insert into clin.lnk_vaccination_course2schedule (fk_course, fk_schedule) values (
	(select pk_course from clin.v_vaccination_courses where indication = 'measles' and recommended_by_name_short = 'STIKO'),
	(select pk from clin.vaccination_schedule where name = 'MMR (STIKO)')
);
-- Mumps
insert into clin.lnk_vaccination_course2schedule (fk_course, fk_schedule) values (
	(select pk_course from clin.v_vaccination_courses where indication = 'mumps' and recommended_by_name_short = 'STIKO'),
	(select pk from clin.vaccination_schedule where name = 'MMR (STIKO)')
);
-- Röteln
insert into clin.lnk_vaccination_course2schedule (fk_course, fk_schedule) values (
	(select pk_course from clin.v_vaccination_courses where indication = 'rubella' and recommended_by_name_short = 'STIKO'),
	(select pk from clin.vaccination_schedule where name = 'MMR (STIKO)')
);

-------------
-- Tetanus --
-------------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='tetanus')
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'3 months'::interval,
	'3 months'::interval,
	'4 weeks'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 5, '4 years'::interval, '5 years'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 6, '9 years'::interval, '17 years'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
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
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='diphtheria')
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values
	(currval('clin.vaccination_course_pk_seq'), 1, '2 months'::interval, '2 months'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 5, '4 years'::interval, '5 years'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	6,
	'9 years'::interval,
	'17 years'::interval,
	'4 weeks'::interval,
	'Impfstoff mit reduziertem Toxoidgehalt (d) verwenden !'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, is_booster, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
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
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='pertussis')
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values
	(currval('clin.vaccination_course_pk_seq'), 1, '2 months'::interval, '2 months'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 2, '3 months'::interval, '3 months'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 3, '4 months'::interval, '4 months'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values
	(currval('clin.vaccination_course_pk_seq'), 4, '11 months'::interval, '14 months'::interval, '4 weeks'::interval);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	5,
	'9 years'::interval,
	'17 years'::interval,
	'5 years'::interval
);

---------
-- HiB --
---------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='haemophilus influenzae b'),
	'falls Mehrfachimpfstoff mit Pertussis (aP), dann Schema wie DTaP/Dt/Td anwenden'
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'4 months'::interval,
	'4 months'::interval,
	'4 weeks'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	3,
	'11 months'::interval,
	'14 months'::interval,
	'4 weeks'::interval
);

----------
-- HepB --
----------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='hepatitis B'),
	'falls Mehrfachimpfstoff mit Pertussis (aP), dann Schema wie DTaP/Dt/Td anwenden,
	 fehlende Grundimmunisierung/Komplettierung zwischen 9 und 17 Jahren'
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'4 months'::interval,
	'4 months'::interval,
	'4 weeks'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	3,
	'11 months'::interval,
	'14 months'::interval,
	'4 weeks'::interval
);

-----------
-- Polio --
-----------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='poliomyelitis'),
	'falls Mehrfachimpfstoff mit Pertussis (aP), dann Schema wie DTaP/Dt/Td anwenden'
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'2 months'::interval,
	'2 months'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'4 months'::interval,
	'4 months'::interval,
	'4 weeks'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	3,
	'11 months'::interval,
	'14 months'::interval,
	'4 weeks'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	4,
	'9 years'::interval,
	'17 years'::interval,
	'5 years'::interval
);

---------------
-- Influenza --
---------------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='influenza')
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'18 years'::interval,
	'jährlich neu von WHO empfohlener Impfstoff'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, is_booster, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	null,
	'19 years'::interval,
	true,
	'1 year'::interval,
	'jährlich neu von WHO empfohlener Impfstoff'
);

------------------
-- Pneumokokken --
------------------
-- Impfplan definieren (STIKO)
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='pneumococcus'),
	'ab 18 Jahre'
);

-- Impfzeitpunkte (STIKO) festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'18 years'::interval,
	'Polysaccharid-Impfstoff'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, is_booster, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	null,
	'24 years'::interval,
	true,
	'6 years'::interval,
	'Polysaccharid-Impfstoff'
);

---------------------
-- Meningokokken C --
---------------------
-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='meningococcus C'),
	'2-12 Monate, Meningokokken C'
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'2 months'::interval,
	'12 months'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'4 months'::interval,
	'14 months'::interval,
	'2 months'::interval
);

-- Impfplan definieren
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	currval('ref_source_pk_seq'),
	(select id from clin.vacc_indication where description='meningococcus C'),
	'ab 12 Monaten, Meningokokken C'
);

-- Impfzeitpunkte festlegen
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'12 months'::interval
);


-- =============================================
-- do simple revision tracking
select log_script_insertion('$RCSfile: STIKO-Impfkalender.sql,v $', '$Revision: 1.20 $');
