-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.patient (
	pk serial primary key,
	fk_identity integer,
	edc date
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-patient-static.sql', '20.0');
