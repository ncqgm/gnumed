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
	r_pt.name_short, r_pt.name_long, r_pt.engine, r_pt.external_version
FROM ref.paperwork_templates r_pt
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN (''L'', ''X'', ''O'', ''T'', ''P'')
		AND
	encode(r_pt.data, ''escape'') ~* (''\$<lastname(::\d+){0,1}>\$|\$<firstname(::\d+){0,1}>\$|\$<title(::\d+){0,1}>\$|\$<date_of_birth(::\d+){0,1}>\$|\$<progress_notes(::\d+){0,1}>\$|\$<soap(::\d+){0,1}>\$|\$<soap_s(::\d+){0,1}>\$|\$<soap_o(::\d+){0,1}>\$|\$<soap_a(::\d+){0,1}>\$|\$<soap_p(::\d+){0,1}>\$|\$<soap_u(::\d+){0,1}>\$|\$<client_version(::\d+){0,1}>\$|\$<current_provider(::\d+){0,1}>\$|\$<primary_praxis_provider(::\d+){0,1}>\$|\$<allergy_state(::\d+){0,1}>\$'')::text
;');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find document templates containing placeholders not conforming to the 1.4 structure';

insert into cfg.report_query (label, cmd) values (
	'Find document templates containing placeholders not conforming to the 1.4 structure',
'SELECT
	r_pt.name_short,
	substring(encode(r_pt.data, ''escape'') from ''\$<[^<:]{1}[^:]+::[^:>]*>\$''::text) as faulty_placeholder,
	r_pt.name_long, r_pt.engine, r_pt.external_version
FROM ref.paperwork_templates r_pt
WHERE
	r_pt.data IS NOT NULL
		AND
	r_pt.engine IN (''L'', ''X'', ''O'', ''T'', ''P'')
		AND
	encode(r_pt.data, ''escape'') ~ ''\$<[^<:]{1}[^:]+::[^:>]*>\$''::text
;');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find keyword expansions possibly containing depreciated $<HINT>$ syntax';

insert into cfg.report_query (label, cmd) values (
	'Find keyword expansions possibly containing depreciated $<HINT>$ syntax',
'SELECT
	keyword,
	substring(expansion from ''\$<[^>]+?>\$''::text) as possibly_faulty_hint
FROM ref.v_keyword_expansions
WHERE
	is_textual
		AND
	NOT is_encrypted
		AND
	expansion ~ ''\$<[^>]+?>\$''
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-cfg-depreciated_placeholders-fixup.sql', '18.4');
