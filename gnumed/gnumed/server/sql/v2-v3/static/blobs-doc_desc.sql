-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - modify blobs.doc_desc
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-doc_desc.sql,v 1.2 2006-11-14 23:52:20 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
alter table blobs.doc_desc
	rename column doc_id to fk_doc;

alter table audit.log_doc_desc
	rename column doc_id to fk_doc;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-doc_desc.sql,v $', '$Revision: 1.2 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: blobs-doc_desc.sql,v $
-- Revision 1.2  2006-11-14 23:52:20  ncq
-- - alter columns in audit tables, too, so auditing works
--
-- Revision 1.1  2006/10/08 09:04:48  ncq
-- - normalize column name
--
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
