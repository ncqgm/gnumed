-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- adjust foreign key
alter table clin.lnk_pat2vaccination_course drop constraint if exists lnk_pat2vaccination_course_fk_patient_fkey cascade;
alter table clin.lnk_pat2vaccination_course drop constraint if exists FK_lnk_pat2vaccination_course_fk_patient cascade;

alter table clin.lnk_pat2vaccination_course
	add constraint FK_lnk_pat2vaccination_course_fk_patient foreign key (fk_patient)
		references clin.patient(fk_identity)
		on update cascade
		on delete cascade
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-lnk_pat2vaccination_course-dynamic.sql', '20.0');
