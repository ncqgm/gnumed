-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- very old:
alter table blobs.doc_obj drop constraint if exists "$1" cascade;
-- medium age:
alter table blobs.doc_obj drop constraint if exists doc_obj_doc_id_fkey cascade;
-- current:
alter table blobs.doc_obj drop constraint if exists doc_obj_fk_doc_fkey cascade;

-- recreate:
alter table blobs.doc_obj
	add foreign key (fk_doc)
		references blobs.doc_med(pk)
		on update cascade
		on delete cascade
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-blobs-doc_obj-fixup_=_16.20.sql', '17.6');
