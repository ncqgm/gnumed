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
comment on column clin.test_org.fk_org_unit is 'link to a unit of an organization more closely defining this lab';

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-test_org-fixup.sql', '19.3');
