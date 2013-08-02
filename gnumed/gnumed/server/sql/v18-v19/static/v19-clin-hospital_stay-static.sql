-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.hospital_stay
	add column fk_org_unit integer;

alter table audit.log_hospital_stay
	add column fk_org_unit integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-hospital_stay-static.sql', '19.0');
