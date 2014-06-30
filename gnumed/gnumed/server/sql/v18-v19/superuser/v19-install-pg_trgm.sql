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
create extension if not exists pg_trgm with schema pg_catalog;

alter extension pg_trgm set schema pg_catalog;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-install-pg_trgm.sql', '19.10');
