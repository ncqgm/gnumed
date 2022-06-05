-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop table if exists cfg.config cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-cfg-drop_old.sql', 'v23');
