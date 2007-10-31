-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v7
-- Target database version: v8
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: blobs-doc_obj.sql,v 1.1 2007-10-31 22:02:45 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table blobs.doc_obj drop constraint doc_obj_doc_id_fkey cascade;
alter table blobs.doc_obj drop constraint doc_obj_fk_doc_fkey cascade;
\set ON_ERROR_STOP 1

alter table blobs.doc_obj
	add foreign key (fk_doc)
		references blobs.doc_med(pk)
		on update cascade
		on delete cascade
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: blobs-doc_obj.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: blobs-doc_obj.sql,v $
-- Revision 1.1  2007-10-31 22:02:45  ncq
-- - cascade deletes seen by fk_doc
--
--
