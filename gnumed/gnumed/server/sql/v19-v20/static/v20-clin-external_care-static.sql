-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.external_care (
	pk serial primary key,
	fk_encounter integer,
	fk_health_issue integer,
	issue text,
	fk_org_unit integer,
	provider text,
	comment text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-external_care-static.sql', '20.0');
