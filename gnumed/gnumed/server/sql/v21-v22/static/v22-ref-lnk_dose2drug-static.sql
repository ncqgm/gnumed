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
drop table if exists ref.lnk_dose2drug cascade;

create table ref.lnk_dose2drug (
	pk serial primary key,
	fk_brand integer,
	fk_dose integer
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-lnk_dose2drug-static.sql', '22.0');
