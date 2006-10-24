-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - drop blobs.xlnk_identity
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-xlnk_identity.sql,v 1.2 2006-10-24 13:10:56 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
drop table blobs.xlnk_identity cascade;

delete from audit.audited_tables where schema = 'blobs' and table_name = 'xlnk_identity';

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-xlnk_identity.sql,v $', '$Revision: 1.2 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: blobs-xlnk_identity.sql,v $
-- Revision 1.2  2006-10-24 13:10:56  ncq
-- - remove from list of audited tables
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
