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
alter table blobs.doc_med
	add column unit_is_receiver boolean
		not null
		default FALSE
	;

alter table audit.log_doc_med
	add column unit_is_receiver boolean;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-blobs-doc_med-static.sql', '22.0');
