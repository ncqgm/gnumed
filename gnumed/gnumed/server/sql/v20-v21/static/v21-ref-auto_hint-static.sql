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
alter table ref.auto_hint
	add column recommendation_query text;

alter table audit.log_auto_hint
	add column recommendation_query text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-ref-auto_hint-static.sql', '21.0');
