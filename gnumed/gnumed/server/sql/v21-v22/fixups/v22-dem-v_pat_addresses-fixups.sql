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
revoke all on dem.v_pat_addresses from public;
grant select on dem.v_pat_addresses to group "gm-doctors";
grant select on dem.v_pat_addresses to group "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-dem-v_pat_addresses-fixups.sql', '22.30');
