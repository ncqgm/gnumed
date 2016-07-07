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
DELETE FROM ref.auto_hint WHERE title = 'Tetanus-Impfg > 10 Jahre (STIKO)';

insert into ref.auto_hint(title, hint, source, lang, query, recommendation_query) values (
	'Tetanus-Impfg > 10 Jahre (STIKO)',
	'Letzte Tetanusimpfung vor mehr als 10 Jahren dokumentiert.',
	'STIKO 2016',
	'de',
	'SELECT (
		-- not deceased
		SELECT deceased is NULL FROM dem.identity WHERE pk = ID_ACTIVE_PATIENT
	) AND NOT EXISTS (
		-- no tetanus shot documented
		SELECT 1 FROM clin.v_pat_vaccs4indication
		WHERE
			pk_patient = ID_ACTIVE_PATIENT
				AND
			indication = ''tetanus''
				AND
			date_given > now() - ''10 years''::interval
		ORDER BY
			date_given DESC
		LIMIT 1
);',
	'SELECT coalesce (
	(SELECT
		''Letzte Tetanusimpfung: '' || to_char(date_given, ''YYYY Mon DD'')
	FROM clin.v_pat_vaccs4indication
	WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		indication = ''tetanus''
	ORDER BY
		date_given DESC
	LIMIT 1),
	''keine Tetanusimpfung dokumentiert''
) as recommendation;'
);

-- --------------------------------------------------------------
SELECT gm.log_script_insertion('v21-ref-auto_hint-tetanus_STIKO.sql', '21.7');
