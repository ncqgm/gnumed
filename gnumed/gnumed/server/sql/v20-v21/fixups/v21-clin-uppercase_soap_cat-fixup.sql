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
UPDATE clin.clin_root_item
	SET soap_cat = lower(soap_cat)
	WHERE
		soap_cat IS DISTINCT FROM NULL
			AND
		soap_cat <> lower(soap_cat)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-uppercase_soap_cat-fixup.sql', '21.11');
