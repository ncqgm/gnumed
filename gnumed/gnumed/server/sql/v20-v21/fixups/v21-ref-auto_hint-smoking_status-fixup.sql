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
DELETE FROM ref.auto_hint WHERE title = 'Outdated smoking status documentation';

INSERT INTO ref.auto_hint(title, hint, source, lang, query, recommendation_query) VALUES (
	'Outdated smoking status documentation',
	'Smoking status was last recorded more than one year ago for this smoker.',
	'AWMF NVL Schädlicher Tabakgebrauch',
	'en',
	'SELECT EXISTS (
		SELECT 1 FROM clin.v_nonbrand_intakes WHERE
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
	'SELECT
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
		clin.v_nonbrand_intakes
	WHERE pk_patient = ID_ACTIVE_PATIENT;'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-ref-auto_hint-smoking_status-fixup.sql', '21.7');
