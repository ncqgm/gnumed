-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find - by name part - organization contact numbers';
insert into cfg.report_query (label, cmd) values (
	'Find - by name part - organization contact numbers',
'-- How to use this query:
-- 1. scroll down to the bottom
-- 2. replace NAME_PART_TO_FIND by a name-part to search for
-- 3. click the [Run] button

SELECT
	d_o.description as organization,
	e_comm.description as contact,
	o_comm.url
FROM dem.org d_o
	INNER JOIN dem.org_unit d_ou ON d_o.pk = d_ou.fk_org
		INNER JOIN dem.lnk_org_unit2comm o_comm ON d_ou.pk = o_comm.fk_org_unit
			INNER JOIN dem.enum_comm_types e_comm ON o_comm.fk_type = e_comm.pk
WHERE
	position(LOWER(''NAME_PART_TO_FIND'') in LOWER(d_o.description)) > 0
ORDER BY
	d_o.description
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-cfg-report_query-fixup.sql', '16.1');
