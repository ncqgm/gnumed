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
-- .status
comment on column clin.test_result.status is 'The result status (say, HL7 OBX 11 Observ result status (#00579, table 0085).';

alter table clin.test_result
	add constraint clin_test_result_sane_status check (
		gm.is_null_or_non_empty_string(status)
	);

drop index if exists clin.idx_test_result_status;

create index idx_test_result_status on clin.test_result(status);

-- --------------------------------------------------------------
-- .source_data
comment on column clin.test_result.source_data is 'The source data for this observation (say, HL7 OBX).';

alter table clin.test_result
	add constraint clin_test_result_sane_source_data check (
		gm.is_null_or_non_empty_string(source_data)
	);

-- --------------------------------------------------------------
-- .val_grouping
comment on column clin.test_result.val_grouping is 'A grouping for related values (say, HL7 OBX Obs Sub ID, think antibiogram).';

alter table clin.test_result
	add constraint clin_test_result_sane_val_grouping check (
		gm.is_null_or_non_empty_string(val_grouping)
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-test_result-dynamic.sql', '20.0');
