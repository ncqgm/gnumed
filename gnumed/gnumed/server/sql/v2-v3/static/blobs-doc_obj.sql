-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - modify blobs.doc_obj
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-doc_obj.sql,v 1.2 2007-09-24 23:31:17 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table blobs.doc_obj
	rename column doc_id to fk_doc;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-doc_obj.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: blobs-doc_obj.sql,v $
-- Revision 1.2  2007-09-24 23:31:17  ncq
-- - remove begin; commit; as it breaks the bootstrapper
--
-- Revision 1.1  2006/10/08 09:05:15  ncq
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
