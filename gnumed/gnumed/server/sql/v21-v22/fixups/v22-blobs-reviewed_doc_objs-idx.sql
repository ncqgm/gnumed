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
drop index if exists blobs.idx_rev_doc_objs_fk_reviewed_row cascade;
create index idx_rev_doc_objs_fk_reviewed_row on blobs.reviewed_doc_objs(fk_reviewed_row);


drop index if exists blobs.idx_rev_doc_objs_fk_reviewer cascade;
create index idx_rev_doc_objs_fk_reviewer on blobs.reviewed_doc_objs(fk_reviewer);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-blobs-reviewed_doc_objs-idx.sql', '22.24');
