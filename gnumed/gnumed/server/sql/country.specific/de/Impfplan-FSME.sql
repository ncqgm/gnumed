-- Projekt GNUmed
-- Impfkalender der Hersteller von Influenza-Impfstoff

-- Quellen: Beipackzettel

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- Impfplan erstellen
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	-1,
	(select id from clin.vacc_indication where description='tick-borne meningoencephalitis'),
	'Normal-Immunisierung (Hersteller)'
);

-- Impfzeitpunkte definieren
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'12 months'::interval,
	'12 years'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'13 months'::interval,
	'12 years'::interval,
	'1 month'::interval,
	'frühestmögliche Serokonversion in 14 Tagen, 1-3 Monate nach 1.Impfung'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	3,
	'22 months'::interval,
	'12 years'::interval,
	'9 months'::interval,
	'9-12 Monate nach 2.Impfung'
);

-- fast path
insert into clin.vaccination_course
	(fk_recommended_by, fk_indication, comment)
values (
	-1,
	(select id from clin.vacc_indication where description='tick-borne meningoencephalitis'),
	'Schnell-Immunisierung (Hersteller)'
);

-- Impfzeitpunkte definieren
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'12 months'::interval,
	'12 years'::interval
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	2,
	'12 months 7 days'::interval,
	'12 years'::interval,
	'7 days'::interval,
	'am Tag 7 nach 1.Impfung, frühestmögliche Serokonversion in 14 Tagen'
);

insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, max_age_due, min_interval, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	3,
	'12 months 21 days'::interval,
	'12 years'::interval,
	'14 days'::interval,
	'am Tag 21, 14 Tage nach 2.Impfung'
);

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: Impfplan-FSME.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: Impfplan-FSME.sql,v $', '$Revision: 1.6 $');
