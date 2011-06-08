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
delete from cfg.report_query where label = 'patients currently taking drug XXX';

insert into cfg.report_query (label, cmd) values (
	'patients currently taking drug XXX',
'SELECT
	vbp.lastnames,
	vbp.preferred,
	vbp.firstnames,
	vbp.pk_identity as pk_patient,
	vpsi.substance,
	vpsi.strength,
	vpsi.brand,
	vpsi.preparation,
	to_char(vpsi.started, ''MM/YYYY'') as started,
	vpsi.seems_inactive,
	vpsi.atc_substance,
	vpsi.atc_brand,
	vpsi.external_code_brand,
	vpsi.external_code_type_brand
FROM
	dem.v_basic_person vbp
		INNER JOIN
	clin.v_pat_substance_intake vpsi
		ON (vpsi.pk_patient = vbp.pk_identity)
WHERE
	vpsi.is_currently_active IS True
		AND
	(
		(lower(''enter desired drug name here'') IN (lower(vpsi.substance), lower(vpsi.brand)))
			OR
		(lower(''enter desired ATC here'') IN (lower(vpsi.atc_substance), lower(vpsi.atc_brand)))
			OR
		(lower(vpsi.external_code_brand) = lower(''enter desired (national) drug ID here''))
	)
ORDER BY
	vbp.lastnames,
	vbp.firstnames
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v14-cfg-report_query-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
