-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
-- --------------------------------------------------------------
-- convert placeholders
UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<lastname>\$',
			'$<lastname::::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<lastname::40>\$',
			'$<lastname::::40>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<firstname>\$',
			'$<firstname::::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<firstname::40>\$',
			'$<firstname::::40>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<title>\$',
			'$<title::::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<progress_notes>\$',
			'$<progress_notes::soapu //%s::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<soap>\$',
			'$<soap::soapu //%s::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<soap_s>\$',
			'$<progress_notes::s//%s::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<soap_o>\$',
			'$<progress_notes::o//%s::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<soap_a>\$',
			'$<progress_notes::a//%s::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<soap_p>\$',
			'$<progress_notes::p//%s::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<soap_u>\$',
			'$<progress_notes::u//%s::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<soap_admin>\$',
			'$<progress_notes:: //%s::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<client_version>\$',
			'$<client_version::::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<current_provider>\$',
			'$<current_provider::::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<primary_praxis_provider>\$',
			'$<primary_praxis_provider::::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<allergy_state>\$',
			'$<allergy_state::::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<date_of_birth>\$',
			'$<date_of_birth::::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<date_of_birth::%Y %B %d>\$',
			'$<date_of_birth::%Y %B %d::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<today::%Y %B %d>\$',
			'$<today::%Y %B %d::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<today::%d\.%B %Y>\$',
			'$<today::%d.%B %Y::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<current_meds_table::latex>\$',
			'$<current_meds_table::latex::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'T')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<current_meds_notes::latex>\$',
			'$<current_meds_notes::latex::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'T')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<adr_street::home>\$',
			'$<adr_street::home::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<adr_number::home>\$',
			'$<adr_number::home::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<adr_postcode::home>\$',
			'$<adr_postcode::home::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<adr_location::home>\$',
			'$<adr_location::home::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'O', 'T', 'P')
;

UPDATE ref.paperwork_templates r_pt SET
	data = decode (
		regexp_replace (
			encode(data, 'escape'),
			'\$<latest_vaccs_table::latex>\$',
			'$<latest_vaccs_table::latex::>$',
			'ig'
		),
		'escape'
	)
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN ('L', 'X', 'T')
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-paperwork_templates-fixup.sql', '18.4');
