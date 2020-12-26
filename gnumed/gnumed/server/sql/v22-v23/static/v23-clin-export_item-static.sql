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
alter table clin.export_item
	add column list_position integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-export_item-static.sql', '23.0');
