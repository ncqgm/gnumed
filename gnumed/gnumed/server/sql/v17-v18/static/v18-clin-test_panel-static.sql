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
create table clin.test_panel (
	pk serial primary key,
	description text,
	comment text,
	pk_test_types integer[]
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-clin-test_panel-static.sql', '18.0');
