-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
--set check_function_bodies to on;

-- --------------------------------------------------------------
select gm.register_notifying_table('blobs'::name, 'reviewed_doc_objs'::name, 'doc_obj_review'::name);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-blobs-reviewed_doc_objs-dynamic.sql', 'Revision 1');

-- ==============================================================
