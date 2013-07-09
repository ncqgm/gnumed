-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_test_type_loinc;
\set ON_ERROR_STOP 1

create index idx_test_type_loinc on clin.test_type(loinc);

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-test_type-dynamic.sql', '19.0');
