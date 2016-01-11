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
drop extension if exists pg_trgm cascade;

create schema pgtrgm;
create extension pg_trgm with schema pgtrgm;

grant usage on schema pgtrgm to "gm-dbo";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-reinstall-pg_trgm.sql', '21.0');
