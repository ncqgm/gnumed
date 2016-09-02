-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
UPDATE ref.auto_hint SET
	query = 'SELECT (
	SELECT
		-- known DOB
		d_i.dob is not NULL
			AND
		-- not deceased
		d_i.deceased is NULL
	FROM
		dem.identity d_i
	WHERE
		d_i.pk = ID_ACTIVE_PATIENT

) AND (
	SELECT
		age(d_i.dob) >= ''35 years''::interval
	FROM
		dem.identity d_i
	WHERE
		d_i.pk = ID_ACTIVE_PATIENT

) AND NOT EXISTS (
	SELECT 1 FROM clin.v_emr_journal
	WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		narrative ~* ''.*checkup.*''
			AND
		age(clin_when) < ''2 years''::interval
);'
WHERE title = 'GKV-Checkup überfällig';

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-ref-GKV_CU-fixup.sql', '21.7');
