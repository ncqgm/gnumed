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
alter table clin.substance_intake
	add column fk_drug_component_new integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-substance_intake-static.sql', '22.0');
