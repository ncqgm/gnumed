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
create table ref.consumable_substance (
	pk serial primary key,
	description text,
	atc_code text,
	amount decimal,
	unit text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-consumable_substance-static.sql', 'Revision: 1.1');

-- ==============================================================
