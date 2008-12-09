-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-blobs-doc_med-static.sql,v 1.1 2008-12-09 21:08:12 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table blobs.doc_med drop column fk_identity cascade;


alter table audit.log_doc_med drop column fk_identity;
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-blobs-doc_med-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-blobs-doc_med-static.sql,v $
-- Revision 1.1  2008-12-09 21:08:12  ncq
-- - drop fk_identity
--
--