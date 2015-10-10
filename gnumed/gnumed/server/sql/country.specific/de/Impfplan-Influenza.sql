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
	(select id from clin.vacc_indication where description='influenza'),
	'>6 Monate, Hersteller'
);

-- Impfzeitpunkte definieren
insert into clin.vaccination_definition
	(fk_course, seq_no, min_age_due, comment)
values (
	currval('clin.vaccination_course_pk_seq'),
	1,
	'6 months'::interval,
	'nie zuvor geimpfte Kinder 4 Wo danach boostern'
);

-- =============================================
-- do simple revision tracking
select log_script_insertion('$RCSfile: Impfplan-Influenza.sql,v $', '$Revision: 1.9 $');
