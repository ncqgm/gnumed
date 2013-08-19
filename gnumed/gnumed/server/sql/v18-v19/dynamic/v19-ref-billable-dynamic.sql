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

grant select, insert, update, delete on
	ref.billable
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-ref-billable-dynamic.sql', '19.0');
