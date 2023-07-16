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
drop index if exists blobs.idx_doc_med_fk_encounter cascade;
create index idx_doc_med_fk_encounter on blobs.doc_med(fk_encounter);


drop index if exists blobs.idx_doc_med_fk_episode cascade;
create index idx_doc_med_fk_episode on blobs.doc_med(fk_episode);


drop index if exists blobs.idx_doc_med_fk_type cascade;
create index idx_doc_med_fk_type on blobs.doc_med(fk_type);


drop index if exists blobs.idx_doc_med_fk_org_unit cascade;
create index idx_doc_med_fk_org_unit on blobs.doc_med(fk_org_unit);


drop index if exists blobs.idx_doc_med_fk_hospital_stay cascade;
create index idx_doc_med_fk_hospital_stay on blobs.doc_med(fk_hospital_stay);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-blobs-doc_med-idx.sql', '22.24');
