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
create table ref.lnk_loinc2substance (
	pk serial primary key,
	fk_substance integer,
	loinc text,
	max_age interval,
	comment text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-lnk_loinc2substance-static.sql', '22.0');
