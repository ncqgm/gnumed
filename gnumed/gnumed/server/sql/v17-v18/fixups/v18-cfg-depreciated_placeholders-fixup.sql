-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find document templates containing depreciated placeholders';

insert into cfg.report_query (label, cmd) values (
	'Find document templates containing depreciated placeholders',
'SELECT
	r_pt.name_short, r_pt.name_long, r_pt.external_version
FROM ref.paperwork_templates r_pt
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN (''L'', ''X'', ''O'', ''T'', ''P'')
		AND
	r_pt.data::text ~* ''(\$<lastname>\$)|(\$<firstname>\$)|(\$<title>\$)|(\$<date_of_birth>\$)|(\$<progress_notes>\$)|(\$<soap>\$)|(\$<soap_s>\$)|(\$<soap_o>\$)|(\$<soap_a>\$)|(\$<soap_p>\$)|(\$<soap_u>\$)|(\$<client_version>\$)|(\$<current_provider>\$)|(\$<primary_praxis_provider>\$)|(\$<allergy_state>\$)''::text
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-cfg-depreciated_placeholders-fixup.sql', '18.4');
