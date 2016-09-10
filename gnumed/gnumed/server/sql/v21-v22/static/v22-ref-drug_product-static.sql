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
alter table ref.branded_drug
	rename to drug_product;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-drug_product-static.sql', '22.0');
