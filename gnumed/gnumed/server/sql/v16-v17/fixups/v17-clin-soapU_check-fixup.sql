-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- clin.clin_root_item
\unset ON_ERROR_STOP
alter table clin.clin_root_item	drop constraint clin_root_item_soap_cat;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-clin-soapU_check-fixup.sql', '17.10');
