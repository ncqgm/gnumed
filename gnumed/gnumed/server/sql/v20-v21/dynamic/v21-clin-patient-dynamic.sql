-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
create or replace function clin.validate_smoking_details(details jsonb)
	returns boolean
	language plpgsql
	as '
BEGIN
	-- cannot ADD/DELETE JSON keys from within PG just yet
	-- so cannot usefully add missing keys

	IF details IS NULL THEN
		RETURN TRUE;
	END IF;

	-- all required fields available ?
	IF (details ?& ARRAY[''quit_when'', ''last_confirmed'', ''comment'']) IS FALSE THEN
		RAISE EXCEPTION
			''clin.validate_smoking_details(details jsonb): must contain <quit_when>, <last_confirmed>, <comment> but contains: [%]'',
			array_to_string(array(select jsonb_object_keys(details)), '','')
			USING ERRCODE = ''check_violation''
		;
		RETURN FALSE;
	END IF;

	-- quit_when is NULL or valid timestamp
	IF (details->>''quit_when'') IS NOT NULL THEN
		PERFORM (details->>''quit_when'')::timestamp with time zone;
	END IF;

	-- last_confirmed is valid timestamp
	PERFORM (details->>''last_confirmed'')::timestamp with time zone;

	-- comment is NULL or not empty
	IF gm.is_null_or_non_empty_string(details->>''comment'') IS FALSE THEN
		RAISE EXCEPTION
			''clin.validate_smoking_details(details jsonb): <comment> not NULL or non-empty''
			USING ERRCODE = ''check_violation''
		;
		RETURN FALSE;
	END IF;
	-- comment is of type STRING
	IF (details->>''comment'') IS DISTINCT FROM NULL THEN
		IF jsonb_typeof(details->''comment'') <> ''string'' THEN
			RAISE EXCEPTION
				''clin.validate_smoking_details(details jsonb): <comment> must be a string but is [%]'',
				jsonb_typeof(details->''comment'')
				USING ERRCODE = ''check_violation''
			;
			RETURN FALSE;
		END IF;
	END IF;

	RETURN TRUE;
END;';


comment on function clin.validate_smoking_details(details jsonb) is
	'This function validates smoking details json content.';

-- --------------------------------------------------------------
comment on column clin.patient.smoking_ever is 'Smoking status: NULL=unknown, FALSE=never, TRUE=now or previously';
comment on column clin.patient.smoking_details is 'Application level details on smoking: .quit_when / .last_confirmed / .details (comment, pack years, n per day, type of consumption)';


alter table clin.patient
	drop constraint if exists clin_patient_sane_smoking_details;

alter table clin.patient
	add constraint clin_patient_sane_smoking_details check (
		(clin.validate_smoking_details(smoking_details) IS TRUE)
			AND
		(
			(
				(smoking_ever IS NOT NULL)
					AND
				(smoking_details IS NOT NULL)
			)
				OR
			(
				(smoking_ever IS NULL)
					AND
				(smoking_details IS NULL)
			)
		)
	);

-- --------------------------------------------------------------
UPDATE clin.patient SET
	smoking_ever = True,
	smoking_details = '{"last_confirmed":"20051111","quit_when":null,"comment":"enjoys an occasional pipe of Old Toby"}'::jsonb
WHERE
	fk_identity = (
		SELECT pk_identity FROM dem.v_persons
		WHERE
			firstnames = 'James Tiberius'
				AND
			lastnames = 'Kirk'
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-patient-dynamic.sql', '21.0');
