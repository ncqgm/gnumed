-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.lnk_pat2vaccination_course
	drop constraint "$1";
alter table clin.lnk_pat2vaccination_course
	drop constraint "lnk_pat2vaccination_course_fk_patient_fkey";
\set ON_ERROR_STOP 1

alter table clin.lnk_pat2vaccination_course
	add foreign key(fk_patient)
		references dem.identity(pk)
		on update cascade
		on delete cascade;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-lnk_pat2vaccination_course.sql,v $', '$Revision: 1.3 $');
