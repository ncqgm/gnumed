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
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.encounter
	drop constraint if exists "$1";
alter table clin.encounter
	drop constraint if exists "encounter_fk_patient_fkey";

alter table clin.encounter
	add foreign key(fk_patient)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-encounter.sql,v $', '$Revision: 1.2 $');
