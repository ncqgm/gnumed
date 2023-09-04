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
-- as recommended by PG:
revoke create on schema public from public;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-revoke_on_public.sql', '23.0');
