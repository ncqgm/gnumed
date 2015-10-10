-- Projekt GNUmed
-- Impfkalender der Firma Wyeth Lederle für Prevenar (Pneumokokken)

-- Quellen: Beipackzettel

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
--delete from lnk_vaccination_definition2course;
--delete from clin.vaccination_definition;
--delete from clin.vaccination_course;

----------------------------
-- Kinder unter 6 Monaten --
----------------------------
-- Impfplan erstellen
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	-1,
	(select id from clin.vacc_indication where description='pneumococcus'),
	'Start <6 Monate, Hersteller'
);

-- Impfzeitpunkte definieren
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'2 months'::interval,
	'6 months'::interval,
	'<6 Monate, Hersteller'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'3 months'::interval,
	'7 months'::interval,
	'4 weeks'::interval,
	'<6 Monate, Hersteller'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	3,
	'4 months'::interval,
	'8 months'::interval,
	'4 weeks'::interval,
	'<6 Monate, Hersteller'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	4,
	'1 year'::interval,
	'2 years'::interval,
	'8 months'::interval,
	'<6 Monate, Hersteller'
);

--------------------------------------
-- Kinder zwischen 7 und 11 Monaten --
--------------------------------------
-- Impfplan erstellen
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	-1,
	(select id from clin.vacc_indication where description='pneumococcus'),
	'Start 7-11 Monate, Hersteller'
);

-- Impfzeitpunkte definieren
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'7 months'::interval,
	'11 months'::interval,
	'7-11 Monate, Hersteller'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'8 months'::interval,
	'12 months'::interval,
	'4 weeks'::interval,
	'7-11 Monate, Hersteller'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	3,
	'1 year'::interval,
	'2 years'::interval,
	'4 weeks'::interval,
	'7-11 Monate, Hersteller'
);

---------------------------------------
-- Kinder zwischen 12 und 23 Monaten --
---------------------------------------
-- Impfplan erstellen
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	-1,
	(select id from clin.vacc_indication where description='pneumococcus'),
	'Start 12-23 Monate, Hersteller'
);

-- Impfzeitpunkte definieren
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'12 months'::interval,
	'23 months'::interval,
	'12-23 Monate, Hersteller'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'14 months'::interval,
	'25 months'::interval,
	'2 month'::interval,
	'12-23 Monate, Hersteller'
);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename like '%Impfplan-Prevenar%';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: Impfplan-Prevenar.sql,v $', '$Revision: 1.12 $');
