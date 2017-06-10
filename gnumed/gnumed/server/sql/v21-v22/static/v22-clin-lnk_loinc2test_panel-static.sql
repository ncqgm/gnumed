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
create table clin.lnk_loinc2test_panel (
	pk serial primary key,
	fk_test_panel integer,
	loinc text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-lnk_loinc2test_panel-static.sql', '22.0');
