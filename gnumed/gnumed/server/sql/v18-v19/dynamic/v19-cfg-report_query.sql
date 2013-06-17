-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'medications: substances taken (regardless of form or strength) across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: substances taken (regardless of form or strength) across all patients',
'SELECT
	substance, count(1) as patient_count
FROM clin.v_substance_intakes
GROUP BY substance
ORDER BY patient_count DESC
;');

delete from cfg.report_query where label = 'medications: substances taken (by form and strength) across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: substances taken (by form and strength) across all patients',
'SELECT
	substance, preparation, amount, unit, count(1) as patient_count
FROM clin.v_substance_intakes
GROUP BY substance, preparation, amount, unit
ORDER BY patient_count DESC
;');


delete from cfg.report_query where label = 'medications: *generic* (non-brand) substances taken (regardless of form or strength) across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: *generic* (non-brand) substances taken (regardless of form or strength) across all patients',
'SELECT
	substance, count(1) as patient_count
FROM clin.v_nonbrand_intakes
GROUP BY substance
ORDER BY patient_count DESC
;');

delete from cfg.report_query where label = 'medications: *generic* (non-brand) substances taken (by form and strength) across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: *generic* (non-brand) substances taken (by form and strength) across all patients',
'SELECT
	substance, preparation, amount, unit, count(1) as patient_count
FROM clin.v_nonbrand_intakes
GROUP BY substance, preparation, amount, unit
ORDER BY patient_count DESC
;');


delete from cfg.report_query where label = 'medications: in-brand (non-generic) substances taken (regardless of form, strength, and brand) across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: in-brand (non-generic) substances taken (regardless of form, strength, and brand) across all patients',
'SELECT
	substance, count(1) as patient_count
FROM clin.v_brand_intakes
GROUP BY substance
ORDER BY patient_count DESC
;');

delete from cfg.report_query where label = 'medications: in-brand (non-generic) substances taken (by form and strength, but regardless of actual brand) across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: in-brand (non-generic) substances taken (by form and strength, but regardless of actual brand) across all patients',
'SELECT
	substance, preparation, amount, unit, count(1) as patient_count
FROM clin.v_brand_intakes
GROUP BY substance, preparation, amount, unit
ORDER BY patient_count DESC
;');


delete from cfg.report_query where label = 'medications: brands taken across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: brands taken across all patients',
'SELECT
	brands_taken.brand, brands_taken.preparation, count(1) as patient_count
FROM (
	SELECT DISTINCT ON (pk_patient)
		brand, preparation
	FROM clin.v_brand_intakes
) AS brands_taken
GROUP BY brands_taken.brand, brands_taken.preparation
ORDER BY patient_count DESC
;');


delete from cfg.report_query where label = 'medications: multi-component brands taken across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: multi-component brands taken across all patients',
'SELECT
	multi_brands_taken.brand, multi_brands_taken.preparation, count(1) as patient_count
FROM (
	SELECT DISTINCT ON (pk_patient)
		c_vpsi.brand, c_vpsi.preparation
	FROM clin.v_brand_intakes c_vpsi
	WHERE
		(SELECT count(r_ls2b.*)
		 FROM ref.lnk_substance2brand r_ls2b
		 WHERE r_ls2b.fk_brand = c_vpsi.pk_brand
		) > 1
) AS multi_brands_taken
GROUP BY multi_brands_taken.brand, multi_brands_taken.preparation
ORDER BY patient_count DESC
;');


delete from cfg.report_query where label = 'medications: single-component brands taken across all patients';
insert into cfg.report_query (label, cmd) values (
	'medications: single-component brands taken across all patients',
'SELECT
	c_vpsi.brand, c_vpsi.preparation, count(c_vpsi.*) as patient_count
FROM clin.v_brand_intakes c_vpsi
WHERE
	(SELECT count(r_ls2b.*)
	 FROM ref.lnk_substance2brand r_ls2b
	 WHERE r_ls2b.fk_brand = c_vpsi.pk_brand
	) = 1
GROUP BY c_vpsi.brand, c_vpsi.preparation
ORDER BY patient_count DESC
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-cfg-report_query.sql', '19.0');
