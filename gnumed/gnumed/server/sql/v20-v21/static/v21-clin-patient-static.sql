-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.patient
	add column smoking_ever boolean;

alter table audit.log_patient
	add column smoking_ever boolean;


alter table clin.patient
	add column smoking_details jsonb;

alter table audit.log_patient
	add column smoking_details jsonb;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-patient-static.sql', '21.0');
