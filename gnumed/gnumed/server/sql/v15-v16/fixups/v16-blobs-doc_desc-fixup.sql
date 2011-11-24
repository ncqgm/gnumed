-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table blobs.doc_desc drop constraint doc_desc_doc_id_text_key cascade;
drop index blobs.idx_doc_desc_fk_doc cascade;
\set ON_ERROR_STOP 1

create index idx_doc_desc_fk_doc on blobs.doc_desc(fk_doc);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-blobs-doc_desc-fixup.sql', '16.5');
