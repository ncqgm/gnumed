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
drop table if exists ref.dose cascade;

create table ref.dose (
	pk serial primary key,
	fk_substance integer,
	amount numeric,
	unit text,
	dose_unit text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-dose-static.sql', '22.0');
