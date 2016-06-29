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
DELETE FROM ref.auto_hint WHERE title = 'Raucher->Spiro (DGP/DGIM)';

insert into ref.auto_hint(title, hint, source, lang, query, recommendation_query) values (
	'Raucher->Spiro (DGP/DGIM)',
	'Raucher sollen mit Spirometrie überwacht werden',
	'"Gemeinsam klug entscheiden" (DGIM: DGP, 2016)',
	'de',
	'-- recently confirmed to be a smoker
SELECT EXISTS (
	SELECT 1 FROM clin.v_substance_intakes WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(atc_substance = ''N07BA01'')
			AND
		(coalesce(harmful_use_type, -1) > IN (1,2))
			AND
		((discontinued IS NULL) OR (discontinued > now()))
			AND
		(last_checked_when > now() - ''1 year''::interval)
-- but no FEV1 documented within the last year
) AND NOT EXISTS (
	SELECT 1 FROM clin.v_test_results WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(
			(unified_loinc = ''20150-9'')
				OR
			(lower(unified_name) = ''fev1'')
				OR
			(lower(unified_abbrev) = ''fev1'')
		)
			AND
		(clin_when > now() - ''1 year''::interval)
);',
	'SELECT (
	SELECT
		''Patient raucht ('' || to_char(last_checked_when, ''YYYY Mon'') || ''), aber ''
	FROM clin.v_substance_intakes WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(atc_substance = ''N07BA01'')
) || (SELECT
	coalesce (
		(SELECT ''die letzte Spirometrie (FEV1 [20150-9)] ist über 1 Jahr her ('' || to_char(clin_when, ''YYYY Mon'') || '').''
		FROM clin.v_test_results WHERE
				(pk_patient = ID_ACTIVE_PATIENT)
					AND
				(
					(unified_loinc = ''20150-9'')
						OR
					(lower(unified_name) = ''fev1'')
						OR
					(lower(unified_abbrev) = ''fev1'')
				)
		)::TEXT,
		''es ist keine Spirometrie (FEV1 [20150-9]) dokumentiert.''::TEXT
	)
) as recommendation;'
);

-- --------------------------------------------------------------
DELETE FROM ref.auto_hint WHERE title = 'Lunge->Pneumokkken-Impfg (DGP/DGIM)';

insert into ref.auto_hint(title, hint, source, lang, query, recommendation_query) values (
	'Lunge->Pneumokkken-Impfg (DGP/DGIM)',
	'Lungenkranke älter 60 sollen eine Pneumokokkenimpfung angeboten bekommen.',
	'"Gemeinsam klug entscheiden" (DGIM: DGP, 2016)',
	'de',
	'-- >60 years
SELECT EXISTS (
	SELECT 1 FROM dem.identity WHERE
		(pk = ID_ACTIVE_PATIENT)
			AND
		(dob < now() - ''60 years''::interval)
) AND EXISTS (
-- Asthma/COPD/Emphysem/Lungenfibrose
SELECT 1 FROM clin.v_problem_list WHERE
	(pk_patient = ID_ACTIVE_PATIENT)
		AND
	(	-- should check ICPC/ICD10
		(problem ilike ''%asthma%'')
			OR
		(problem ilike ''%COPD%'')
			OR
		(problem ilike ''%emphysem%'')
			OR
		(
			(problem ilike ''%fibros%'')
				AND
			(
				(problem ilike ''%lung%'')
					OR
				(problem ilike ''%pulmon%'')
			)
		)
	)
) AND NOT EXISTS (
-- keine Impfung Pneumokokken
SELECT 1 FROM clin.v_pat_vaccs4indication WHERE
	(pk_patient = ID_ACTIVE_PATIENT)
		AND
	(indication = ''pneumococcus'')
)',
	'SELECT
(	-- explain
	SELECT E''Es ist keine Impfung gegen Pneumokokken dokumentiert.\n\n''
		|| E''Es sollte eine Impfung angeboten werden, weil\n''
		-- age
		|| '' das Alter ('' || trim(leading ''0'' from to_char(justify_interval(now() - dob), ''YYY'')) || E'') > 60 Jahre ist und\n''
	FROM dem.identity WHERE pk = ID_ACTIVE_PATIENT
) || (
	-- problem
	SELECT '' ein Lungenproblem "'' || problem || ''" dokumentiert ist''
	FROM clin.v_problem_list WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(	-- should check ICPC/ICD10
			(problem ilike ''%asthma%'')
				OR
			(problem ilike ''%COPD%'')
				OR
			(problem ilike ''%emphysem%'')
				OR
			(
				(problem ilike ''%fibros%'')
					AND
				(
					(problem ilike ''%lung%'')
						OR
					(problem ilike ''%pulmon%'')
				)
			)
		)
)'
);

-- --------------------------------------------------------------
DELETE FROM ref.auto_hint WHERE title = 'Lunge->Influenza-Impfg (DGP/DGIM)';

insert into ref.auto_hint(title, hint, source, lang, query, recommendation_query) values (
	'Lunge->Influenza-Impfg (DGP/DGIM)',
	'Lungenkranke älter 60 sollen eine Influenzaimpfung angeboten bekommen.',
	'"Gemeinsam klug entscheiden" (DGIM: DGP, 2016)',
	'de',
	'
SELECT
	-- beyond August ? -> probably only valid on the Northern Hemisphere
	(extract(month from now()) > 8)
AND EXISTS (
	-- >60 years
	SELECT 1 FROM dem.identity WHERE
		(pk = ID_ACTIVE_PATIENT)
			AND
		(dob < now() - ''60 years''::interval)
) AND EXISTS (
-- Asthma/COPD/Emphysem/Lungenfibrose
SELECT 1 FROM clin.v_problem_list WHERE
	(pk_patient = ID_ACTIVE_PATIENT)
		AND
	(	-- should check ICPC/ICD10
		(problem ilike ''%asthma%'')
			OR
		(problem ilike ''%COPD%'')
			OR
		(problem ilike ''%emphysem%'')
			OR
		(
			(problem ilike ''%fibros%'')
				AND
			(
				(problem ilike ''%lung%'')
					OR
				(problem ilike ''%pulmon%'')
			)
		)
	)
) AND NOT EXISTS (
-- keine Impfung Influenza in den letzten 6 Monaten rückblickend, falls wir im September sind
SELECT 1 FROM clin.v_pat_vaccs4indication WHERE
	(pk_patient = ID_ACTIVE_PATIENT)
		AND
	(indication = ''influenza (seasonal)'')
		AND
	date_given > now() - ''6 months''::interval
ORDER BY
	date_given DESC
LIMIT 1
)',
	'SELECT
(	-- explain
	SELECT E''Es ist in den letzten 6 Monaten keine Impfung gegen Influenza dokumentiert.\n\n''
		|| E''Es sollte eine Impfung angeboten werden, weil\n''
		-- age
		|| '' das Alter ('' || trim(leading ''0'' from to_char(justify_interval(now() - dob), ''YYY'')) || E'') > 60 Jahre ist und\n''
	FROM dem.identity WHERE pk = ID_ACTIVE_PATIENT
) || (
	-- problem
	SELECT '' ein Lungenproblem "'' || problem || ''" dokumentiert ist''
	FROM clin.v_problem_list WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(	-- should check ICPC/ICD10
			(problem ilike ''%asthma%'')
				OR
			(problem ilike ''%COPD%'')
				OR
			(problem ilike ''%emphysem%'')
				OR
			(
				(problem ilike ''%fibros%'')
					AND
				(
					(problem ilike ''%lung%'')
						OR
					(problem ilike ''%pulmon%'')
				)
			)
		)
)'
);

-- --------------------------------------------------------------
DELETE FROM ref.auto_hint WHERE title = 'O²-Gabe->BGA/SpO² (DGP/DGIM)';

insert into ref.auto_hint(title, hint, source, lang, query, recommendation_query) values (
	'O²-Gabe->BGA/SpO² (DGP/DGIM)',
	'Bei ambulanter O²-Therapie soll aller 3 Monate die Indikation geprüft werden.',
	'"Gemeinsam klug entscheiden" (DGIM: DGP, 2016)',
	'de',
	-- query
	'SELECT EXISTS (
	-- takes oxygen
	SELECT 1 FROM clin.v_substance_intakes WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(atc_substance = ''V03AN01'')	-- oxygen
			AND
		((discontinued IS NULL) OR (discontinued > now()))
) AND NOT EXISTS (
	-- no BGA or SpO2 within last 3 months
	SELECT 1 FROM clin.v_test_results WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(unified_loinc IN (select code from ref.loinc where term ilike ''%oxygen%'' and term ilike ''%pressure%''))
			AND
		(clin_when > now() - ''3 months''::interval)
);',
	-- recommendation query
	'
SELECT coalesce (
	(SELECT
		''Die Hypoxämie wurde zuletzt im '' || to_char(clin_when, ''Mon YYYY'') || '' überprüft.''
	FROM clin.v_test_results WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(unified_loinc IN (select code from ref.loinc where term ilike ''%oxygen%'' and term ilike ''%pressure%''))
	ORDER BY
		clin_when DESC
	LIMIT 1
	)::text,
	(SELECT ''Es ist keine Überprüfung der Hypoxämie in den letzten 3 Monaten dokumentiert.''::text)
);'
);

-- --------------------------------------------------------------
SELECT gm.log_script_insertion('v21-ref-auto_hint-klug_entscheiden_pulmo.sql', '21.7');
