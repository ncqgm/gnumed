-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table de_de.insurance_card (
	pk serial primary key,
	fk_identity integer,
	formatted_dob text,
	valid_until date,
	presented timestamp with time zone,
	invalidated date,
	raw_data json
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-de_de-insurance_card-static.sql', '20.0');
