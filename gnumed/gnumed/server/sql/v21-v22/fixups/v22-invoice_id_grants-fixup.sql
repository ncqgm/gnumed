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
-- needed for invoice ID uniqueness checks
GRANT SELECT (invoice_id) ON audit.log_bill TO "gm-doctors" ;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-invoice_id_grants-fixup.sql', '22.7');
