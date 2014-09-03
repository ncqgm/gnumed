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
delete from cfg.report_query where label = 'bills: total sum of unwritten bills';
insert into cfg.report_query (label, cmd) values (
	'bills: total sum of unwritten bills',
'SELECT coalesce((
	SELECT
		sum(total_amount_with_vat)
	FROM
		bill.v_bills
	WHERE
		close_date IS NULL
			AND
		apply_vat IS TRUE
), 0) + coalesce((
	SELECT
		sum(total_amount)
	FROM
		bill.v_bills
	WHERE
		close_date IS NULL
			AND
		apply_vat IS FALSE
), 0)');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'bills: monthly total sums of written bills with VAT';
insert into cfg.report_query (label, cmd) values (
	'bills: monthly total sums of written bills with VAT',
'SELECT
	to_char(date_trunc(''month'', close_date), ''YYYY Month''::text) AS close_month_formatted,
	sum(total_amount_with_vat),
	date_trunc(''month'', close_date) AS close_month
FROM bill.v_bills
WHERE
	close_date IS NOT NULL
		AND
	apply_vat IS TRUE
GROUP BY date_trunc(''month'', close_date)
ORDER BY close_month
');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'bills: monthly total sums of written bills without VAT';
insert into cfg.report_query (label, cmd) values (
	'bills: monthly total sums of written bills without VAT',
'SELECT
	to_char(date_trunc(''month'', close_date), ''YYYY Month''::text) AS close_month_formatted,
	sum(total_amount_with_vat),
	date_trunc(''month'', close_date) AS close_month
FROM bill.v_bills
WHERE
	close_date IS NOT NULL
		AND
	apply_vat IS FALSE
GROUP BY date_trunc(''month'', close_date)
ORDER BY close_month
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-cfg-report_query.sql', '20.0');
