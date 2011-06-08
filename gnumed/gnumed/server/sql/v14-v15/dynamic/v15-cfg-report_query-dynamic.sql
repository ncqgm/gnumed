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
-- find patients by drug
delete from cfg.report_query where label = 'patients with a specific tag';

insert into cfg.report_query (label, cmd) values (
	'patients with a specific tag',
'SELECT
	vbp.lastnames,
	vbp.preferred,
	vbp.firstnames,
	vit.l10n_description as tag,
	coalesce(vit.comment, '''') as comment,
	vbp.pk_identity as pk_patient
FROM
	dem.v_basic_person vbp
		INNER JOIN
	dem.v_identity_tags vit
		ON (vbp.pk_identity = vit.pk_identity)
WHERE
	vit.l10n_description = ''XXX''
ORDER BY
	vbp.lastnames,
	vbp.firstnames
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-cfg-report_query-dynamic.sql', 'Revision: 1.1');

-- ==============================================================
