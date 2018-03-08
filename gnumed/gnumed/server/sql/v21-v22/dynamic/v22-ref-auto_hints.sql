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
update ref.auto_hint set
	popup_type = 1,
	highlight_as_priority = True,
	query = 'SELECT EXISTS (
	-- substance check
	SELECT 1 FROM clin.v_substance_intakes WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		-- on Sartan or ACEI
		(
			substance ~* ''.*sartan.*''
				OR
			substance ~* ''.*angiotensin.*''
				OR
			substance ~ ''.*ACE.*''
				OR
			substance ~* ''.+pril.*''
				OR
			atc_drug ~* ''^C09.*''
				OR
			atc_substance ~* ''^C09.*''
	)
) AND EXISTS (
	-- pregnancy check
	SELECT 1 FROM clin.patient WHERE
		fk_identity = ID_ACTIVE_PATIENT
			AND
		coalesce(edc BETWEEN now() - ''1 month''::interval AND now() + ''11 months''::interval, FALSE)
);'
where
	title = 'Contraindication: ACEI/Sartan <-> Pregnancy'
;

-- --------------------------------------------------------------
UPDATE ref.auto_hint SET
	popup_type = 2,
	highlight_as_priority = False,
	query = 'SELECT NOT EXISTS (
	SELECT 1 FROM clin.v_substance_intakes WHERE pk_patient = ID_ACTIVE_PATIENT AND atc_substance = ''N07BA01'' AND harmful_use_type IS NOT NULL
	);'
WHERE title = 'Lack of smoking status documentation';

-- --------------------------------------------------------------
UPDATE ref.auto_hint SET
	popup_type = 0,
	highlight_as_priority = False,
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
DELETE FROM ref.auto_hint WHERE title = 'test results w/o LOINC';

INSERT INTO ref.auto_hint(title, hint, source, lang, popup_type, highlight_as_priority, query, recommendation_query) VALUES (
	'test results w/o LOINC',
	'There are test results w/o attached LOINC for this patient. Such results cannot be used in clinical decision support.',
	'GNUmed team',
	'en',
	0,
	FALSE,
	'SELECT count(1) > 0 FROM clin.v_test_results
	WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		unified_loinc IS NULL;',
	'SELECT string_agg (
			DISTINCT ''#'' || pk_test_type::text || '': '' || name_tt || '' ('' || abbrev_tt || '')'',
			E''\n''
	) AS recommendation
	FROM clin.v_test_results
	WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		unified_loinc IS NULL;'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-v_auto_hints.sql', '22.0');
