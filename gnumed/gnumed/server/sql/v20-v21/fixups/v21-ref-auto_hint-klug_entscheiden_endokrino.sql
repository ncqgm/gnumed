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
DELETE FROM ref.auto_hint WHERE title = 'Schwangerschaft->Jod (DGE/DGIM)';

insert into ref.auto_hint(title, hint, source, lang, query, recommendation_query) values (
	'Schwangerschaft->Jod (DGE/DGIM)',
	'Schwangeren soll eine Jodsupplementation angeboten werden.',
	'"Gemeinsam klug entscheiden" (DGIM: DGE, 2016)',
	'de',
	'-- pregnancy check
SELECT EXISTS (
	SELECT 1 FROM clin.patient WHERE
		fk_identity = ID_ACTIVE_PATIENT
			AND
		coalesce(edc BETWEEN now() - ''1 month''::interval AND now() + ''11 months''::interval, FALSE)
-- but no jod in medication
) AND NOT EXISTS (
	SELECT 1 FROM clin.v_substance_intakes WHERE
		(pk_patient = ID_ACTIVE_PATIENT)
			AND
		-- iodine
		(atc_substance = ''D08AG03'')
			AND
		((discontinued IS NULL) OR (discontinued > now()))
	);',
	'SELECT
		''Patientin ist schwanger (''
			|| ''Termin: ''
			|| to_char(edc, ''YYYY Mon DD'')
			|| ''), nimmt aber kein Jod [D08AG03].''
		as recommendation
	FROM clin.patient
	WHERE fk_identity = ID_ACTIVE_PATIENT;
');

-- --------------------------------------------------------------
SELECT gm.log_script_insertion('v21-ref-auto_hint-klug_entscheiden_endokrino.sql', '21.7');
