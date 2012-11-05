-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
-- very old:
alter table blobs.doc_obj drop constraint "$1" cascade;
-- medium age:
alter table blobs.doc_obj drop constraint doc_obj_doc_id_fkey cascade;
-- current:
alter table blobs.doc_obj drop constraint doc_obj_fk_doc_fkey cascade;
\set ON_ERROR_STOP 1

-- recreate:
alter table blobs.doc_obj
	add foreign key (fk_doc)
		references blobs.doc_med(pk)
		on update cascade
		on delete cascade
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-blobs-doc_obj-fixup.sql', '16.20');
