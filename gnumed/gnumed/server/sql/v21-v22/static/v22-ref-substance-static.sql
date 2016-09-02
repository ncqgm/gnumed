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
create table ref.substance (
	pk serial primary key,
	description text,
	atc text,
	intake_instructions text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-substance-static.sql', '22.0');
