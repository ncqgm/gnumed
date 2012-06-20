-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'patients whose narrative contains a certain coded term';

delete from cfg.report_query where label = 'patients whose EMR contains a certain coded term';
insert into cfg.report_query (label, cmd) values (
	'patients whose EMR contains a certain coded term',
'SELECT * FROM
	clin.v_linked_codes c_vlc
		INNER JOIN clin.v_pat_items d_vpi ON (d_vpi.pk_item = c_vlc.pk_item)
			INNER JOIN dem.v_basic_person d_vbp ON (d_vbp.pk_identity = d_vpi.pk_patient)
WHERE
	c_vlc.code = ''put the code here''
	-- specify a coding system here
	--AND c_vlc.name_long = ''...''
	-- specify a number of SOAP categories here
	--AND c_vpi.soap_cat IN (''s'', ''o'', ''a'', ''p'', NULL)
');

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find - by name part - organization contact numbers and address';
insert into cfg.report_query (label, cmd) values (
	'Find - by name part - organization contact numbers and address',
'-- How to use this query:
-- 1. scroll down to the bottom
-- 2. replace NAME_PART_TO_FIND by a name-part to search for
-- 3. click the [Run] button

SELECT
	d_o.description as organization,
	e_comm.description as contact,
	o_comm.url,
	d_a.subunit as suite,
	d_a.number as addr,
	d_s.name as street,
	d_a.aux_street aux,
	d_u.name as community,
	d_state.code as prov,
	d_s.postcode as postal
FROM dem.org d_o
	INNER JOIN dem.org_unit d_ou ON d_o.pk = d_ou.fk_org
		INNER JOIN dem.lnk_org_unit2comm o_comm ON d_ou.pk = o_comm.fk_org_unit
			INNER JOIN dem.enum_comm_types e_comm ON o_comm.fk_type = e_comm.pk
				INNER JOIN dem.address d_a ON d_ou.fk_address = d_a.id
					INNER JOIN dem.street d_s ON d_a.id_street = d_s.id
						INNER JOIN dem.urb d_u ON d_s.id_urb = d_u.id
							INNER JOIN dem.state d_state ON d_u.id_state = d_state.id
								INNER JOIN dem.country d_c ON d_state.country = d_c.code
WHERE
	position(LOWER(''NAME_PART_TO_FIND'') in LOWER(d_o.description)) > 0
ORDER BY
	d_o.description
;');

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
select gm.log_script_insertion('v16-cfg-report_query.sql', '16.0');

-- ==============================================================
