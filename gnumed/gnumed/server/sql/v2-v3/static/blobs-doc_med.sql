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
-- $Id: blobs-doc_med.sql,v 1.4 2006-11-14 23:52:20 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
-- patient_id -> fk_identity
alter table blobs.doc_med
	drop constraint "$1";
alter table blobs.doc_med
	drop constraint "doc_med_patient_id_fkey";
\set ON_ERROR_STOP 1

alter table blobs.doc_med
	rename column patient_id to fk_identity;

alter table audit.log_doc_med
	rename column patient_id to fk_identity;

alter table blobs.doc_med
	add foreign key (fk_identity)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- type -> fk_type
alter table blobs.doc_med
	rename column type to fk_type;

alter table audit.log_doc_med
	rename column type to fk_type;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-doc_med.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: blobs-doc_med.sql,v $
-- Revision 1.4  2006-11-14 23:52:20  ncq
-- - alter columns in audit tables, too, so auditing works
--
-- Revision 1.3  2006/10/28 12:22:48  ncq
-- - 8.1 prides itself in naming FKs differently -- better -- but makes
--   changing auto-named foreign keys a pain
--
-- Revision 1.2  2006/10/08 09:15:17  ncq
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
