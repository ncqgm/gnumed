-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.patient.smoking_ever is 'Smoking status: NULL=unknown, FALSE=never, TRUE=now or previously';
comment on column clin.patient.smoking_details is 'Application level details on smoking: .quit_when / .last_checked / .details (comment, pack years, n per day, type of consumption)';


alter table clin.patient
	drop constraint if exists clin_patient_sane_smoking_details;

alter table clin.patient
	add constraint clin_patient_sane_smoking_details check (
		((smoking_ever IS NULL) AND (smoking_details IS NULL))
			OR
		(smoking_details IS NOT NULL)
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-patient-dynamic.sql', '21.0');
