-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - drop clin.xlnk_identity
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-xlnk_identity.sql,v 1.1 2006-10-24 13:08:25 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
drop table clin.xlnk_identity;

delete from audit.audited_tables where schema = 'clin' and table_name = 'xlnk_identity';

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-xlnk_identity.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: clin-xlnk_identity.sql,v $
-- Revision 1.1  2006-10-24 13:08:25  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
