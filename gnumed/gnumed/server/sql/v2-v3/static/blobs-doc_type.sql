-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - clean up blobs.doc_type
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-doc_type.sql,v 1.2 2007-09-24 23:31:17 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- sanity check
select 1 from ref.document_type;

-- remove those from schema blobs that are not in use
delete from blobs.doc_type where
	not is_user and
	not exists (select 1 from blobs.doc_med dm where dm.type=blobs.doc_type.pk);
-- not needed anymore
alter table blobs.doc_type drop column is_user cascade;

-- --------------------------------------------------------------
grant select, insert, update, delete on blobs.doc_type to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-doc_type.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: blobs-doc_type.sql,v $
-- Revision 1.2  2007-09-24 23:31:17  ncq
-- - remove begin; commit; as it breaks the bootstrapper
--
-- Revision 1.1  2006/09/26 14:47:53  ncq
-- - those live here now
--
-- Revision 1.1  2006/09/18 17:29:14  ncq
-- - move unused entries to ref.documeent_type
-- - drop is_user
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
