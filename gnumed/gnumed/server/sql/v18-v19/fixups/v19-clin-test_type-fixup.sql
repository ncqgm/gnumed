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
comment on column clin.test_type.conversion_unit is 'The chosen reference unit for this test type, preferably SI, used for comparing results delivered in differing units. This does not relate to what unit the test provider delivers results in but rather the unit we think those results need to be converted to in order to be comparable to OTHER results.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-test_type-fixup.sql', '19.3');
