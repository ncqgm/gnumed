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
select audit.register_table_for_auditing('blobs'::name, 'reviewed_doc_objs'::name);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-blobs-reviewed_doc_objs.sql', 'v23');
