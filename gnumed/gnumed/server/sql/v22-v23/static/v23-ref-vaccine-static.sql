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
alter table ref.vaccine
	add column atc gm.nonempty_text;


alter table audit.log_vaccine
	add column atc text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-vaccine-static.sql', '23.0');
