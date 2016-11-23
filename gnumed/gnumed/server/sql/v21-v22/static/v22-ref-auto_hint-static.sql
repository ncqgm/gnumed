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
	add column popup_type integer;

alter table audit.log_auto_hint
	add column popup_type integer;


alter table ref.auto_hint
	add column highlight_as_priority boolean;

alter table audit.log_auto_hint
	add column highlight_as_priority boolean;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-auto_hint-static.sql', '22.0');
