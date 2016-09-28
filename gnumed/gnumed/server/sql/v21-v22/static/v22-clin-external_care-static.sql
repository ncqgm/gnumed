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
alter table clin.external_care
	add column inactive boolean
		not NULL
		default FALSE
	;

alter table audit.log_external_care
	add column inactive boolean;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-external_care-static.sql', '22.0');
