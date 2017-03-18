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
drop table if exists clin.vaccine_batches cascade;

delete from audit.audited_tables
where
	schema = 'clin'
		and
	table_name = 'vaccine_batches';

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-vaccine_batches-dynamic.sql', '22.0');
