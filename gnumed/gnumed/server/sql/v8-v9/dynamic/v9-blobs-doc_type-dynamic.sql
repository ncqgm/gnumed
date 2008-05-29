-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-blobs-doc_type-dynamic.sql,v 1.1 2008-05-29 15:12:41 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.add_table_for_notifies('blobs', 'doc_type');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-blobs-doc_type-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-blobs-doc_type-dynamic.sql,v $
-- Revision 1.1  2008-05-29 15:12:41  ncq
-- - add signal to blobs.doc_type
--
--