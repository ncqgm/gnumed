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
update clin.procedure set
	is_ongoing = False
where
	is_ongoing is True
		and
	clin_end is not null
		and
	clin_end < (now() + '15 minutes'::interval)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-procedure-fixup.sql', '20.11');
