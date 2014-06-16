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
select pg_available_extensions();

create extension if not exists pg_trgm;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-install-pg_trgm.sql', '19.9');
