-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - modify blobs.doc_med
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-doc_med.sql,v 1.4 2006-11-14 23:52:20 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- patient_id -> fk_identity
alter table blobs.doc_med
	drop constraint if exists "$1";
alter table blobs.doc_med
	drop constraint if exists "doc_med_patient_id_fkey";

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
