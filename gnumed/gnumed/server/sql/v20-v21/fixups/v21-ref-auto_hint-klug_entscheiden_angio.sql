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
DELETE FROM ref.auto_hint WHERE title = 'Screening Bauchaortenaneurysma (DGA/DGIM)';

INSERT INTO ref.auto_hint(title, hint, source, lang, query, recommendation_query) VALUES (
	'Screening Bauchaortenaneurysma (DGA/DGIM)',
	'Männern >65J soll Sonographie auf Bauchaortenaneurysma angeboten werden.',
	'"Gemeinsam klug entscheiden" (DGIM: DGA, 2016)',
	'de',
	'SELECT
(		-- male
	SELECT gender IN (''m'',''tm'')
	FROM dem.identity WHERE pk = ID_ACTIVE_PATIENT
) AND (
		-- >65 years
	SELECT dob < now() - ''65 years''::interval
	FROM dem.identity WHERE pk = ID_ACTIVE_PATIENT
) AND NOT EXISTS (
		-- no procedure ''abdo/bauch ultras/sono'' after 65th birthday
	SELECT 1 FROM clin.v_procedures WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		(
			(performed_procedure ILIKE ''%ultras%'')
				OR
			(performed_procedure ILIKE ''%sono%'')
		)
			AND
		(
			(performed_procedure ILIKE ''%bauch%'')
				OR
			(performed_procedure ILIKE ''%abdo%'')
		)
			AND
		(clin_when > (SELECT dob + ''65 years''::interval FROM dem.idenity WHERE pk = ID_ACTIVE_PATIENT))
	);',
	'SELECT
		''Männlicher Patient (>65 Jahre), noch keine Maßnahme "Ultraschall des Abdomens" (als Screening auf Bauchaortenaneurysma) dokumentiert.''
	AS recommendation;'
);

-- --------------------------------------------------------------
SELECT gm.log_script_insertion('v21-ref-auto_hint-klug_entscheiden_angio.sql', '21.7');
