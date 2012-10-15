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
drop table clin.lnk_ttype2unified_type cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-clin-lnk_ttype2unified_type-static.sql', '18.0');
