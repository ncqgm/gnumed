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
alter table dem.staff
	add column public_key gm.nonempty_text;

alter table audit.log_staff
	add column public_key gm.nonempty_text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-staff-static.sql', '23.0');
