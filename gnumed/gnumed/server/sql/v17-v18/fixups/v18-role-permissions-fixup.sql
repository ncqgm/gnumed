-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- "gm-doctors"
-- --------------------------------------------------------------
alter group "gm-public" add user "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-role-permissions-fixup.sql', '18.1');
