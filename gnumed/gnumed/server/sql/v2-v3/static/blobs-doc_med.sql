-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - modify blobs.doc_med
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-doc_med.sql,v 1.2 2006-10-08 09:15:17 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
-- patient_id -> fk_identity
alter table blobs.doc_med
	drop constraint "$1";

alter table blobs.doc_med
	rename column patient_id to fk_identity;

alter table blobs.doc_med
	add foreign key (fk_identity)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- type -> fk_type
alter table blobs.doc_med
	rename column type to fk_type;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-doc_med.sql,v $', '$Revision: 1.2 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: blobs-doc_med.sql,v $
-- Revision 1.2  2006-10-08 09:15:17  ncq
-- - type -> fk_type
--
-- Revision 1.1  2006/09/26 14:47:53  ncq
-- - those live here now
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
