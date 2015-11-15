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
select gm.register_notifying_table('dem', 'lnk_identity2ext_id');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-external_id-dynamic.sql', '21.0');
