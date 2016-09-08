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
	query = 'SELECT NOT EXISTS (
	SELECT 1 FROM clin.v_substance_intakes WHERE pk_patient = ID_ACTIVE_PATIENT AND atc_substance = ''N07BA01'' AND harmful_use_type IS NOT NULL
	);'
WHERE title = 'Lack of smoking status documentation';

-- --------------------------------------------------------------
UPDATE ref.auto_hint SET
	query = 'SELECT EXISTS (
	SELECT 1 FROM clin.v_substance_intakes WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(atc_substance = ''N07BA01'')
			AND
		(coalesce(harmful_use_type, -1) IN (1,2))
			AND
		((discontinued IS NULL) OR (discontinued > now()))
			AND
		(last_checked_when < now() - ''1 year''::interval)
	);',
	recommendation_query = 'SELECT
	_(''Smoking status'') || E''\n''
	|| '' '' || _(''Last checked:'') || '' '' || to_char(last_checked_when, ''Mon YYYY'')
	|| (case
			when harmful_use_type = 1 then E''\n'' || _(''harmful use'')
			when harmful_use_type = 2 then E''\n'' || _(''addiction'')
			when harmful_use_type = 3 then E''\n'' || _(''previous addiction'')
		end)
	|| coalesce(E''\n '' || _(''Quit date:'') || '' '' || to_char(discontinued, ''YYYY Mon DD''), '''')
	|| coalesce(E''\n '' || _(''Notes:'') || '' '' || notes, '''')
FROM
	clin.v_substance_intakes
WHERE pk_patient = ID_ACTIVE_PATIENT;'
WHERE title = 'Outdated smoking status documentation';

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-auto_hint-smoking_status.sql', '22.0');
