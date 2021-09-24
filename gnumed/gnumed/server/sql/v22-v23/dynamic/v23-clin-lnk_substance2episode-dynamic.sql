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
drop table if exists clin.lnk_substance2episode cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-lnk_substance2episode-dynamic.sql', '23.0');
