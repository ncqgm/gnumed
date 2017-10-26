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
select 'no-op SELECT such that the bootstrapper is run and forces SQL_INHERITANCE back to DEFAULT if on PG <10';

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-db-sql_inheritance-fixup.sql', '21.15');
