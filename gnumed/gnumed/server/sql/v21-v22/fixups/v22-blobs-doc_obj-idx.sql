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
drop index if exists blobs.idx_doc_obj_fk_doc cascade;
create index idx_doc_obj_fk_doc on blobs.doc_obj(fk_doc);


drop index if exists blobs.idx_doc_obj_fk_intended_reviewer cascade;
create index idx_doc_obj_fk_intended_reviewer on blobs.doc_obj(fk_intended_reviewer);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-blobs-doc_obj-idx.sql', '22.24');
