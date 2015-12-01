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
	add column fk_org_unit integer;

alter table audit.log_doc_med
	add column fk_org_unit integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-blobs-doc_med-static.sql', '21.0');
