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
-- in v17 add: ", INHERIT FALSE, SET FALSE"
GRANT "gnumed_v22" TO "gm-dbo" WITH ADMIN OPTION;
GRANT "gm-logins" TO "gm-dbo" WITH ADMIN OPTION;
GRANT "gm-doctors" TO "gm-dbo" WITH ADMIN OPTION;
GRANT "gm-public" TO "gm-dbo" WITH ADMIN OPTION;
GRANT "gm-staff" TO "gm-dbo" WITH ADMIN OPTION;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-gm-dbo_grants-fixup.sql', '22.32');
