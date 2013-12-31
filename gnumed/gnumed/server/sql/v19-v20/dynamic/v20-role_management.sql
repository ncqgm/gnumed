-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
grant "gm-staff" to "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-role_management.sql', '20.0');
