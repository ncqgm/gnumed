-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find duplicate regions';

insert into cfg.report_query (label, cmd) values (
	'Find duplicate regions',
'SELECT
	name AS region,
	code,
	country,
	id AS pk
FROM
	dem.state
WHERE
	code || lower(name) || lower(country) IN (
		SELECT
			s.code || lower(s.name) || lower(s.country)
		FROM
			dem.state s
		GROUP BY
			s.code || lower(s.name) || lower(s.country)
		HAVING
			count(*) > 1
	)
ORDER BY
	lower(name),
	lower(country),
	code
;');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find duplicate streets';

insert into cfg.report_query (label, cmd) values (
	'Find duplicate streets',
'SELECT
	name AS street,
	postcode,
	id AS pk
FROM
	dem.street
WHERE
	id_urb || lower(name) || lower(postcode) IN (
		SELECT
			s.id_urb || lower(name) || lower(postcode)
		FROM
			dem.street s
		GROUP BY
			s.id_urb || lower(s.name) || lower(s.postcode)
		HAVING
			count(*) > 1
	)
ORDER BY
	id_urb,
	lower(name),
	lower (postcode)
;');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find duplicate communities';

insert into cfg.report_query (label, cmd) values (
	'Find duplicate communities',
'SELECT
	name AS community,
	postcode,
	id AS pk
FROM
	dem.urb
WHERE
	id_state || lower(name) || lower(postcode) in (
		SELECT
			u.id_state || lower(u.name) || lower(u.postcode)
		FROM
			dem.urb u
		GROUP BY
			u.id_state || lower(u.name) || lower(u.postcode)
		HAVING
			count(*) > 1
	)
ORDER BY
	id_state,
	lower(name),
	lower(postcode)
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-cfg-report_query-find_dupes.sql', '15.11');
