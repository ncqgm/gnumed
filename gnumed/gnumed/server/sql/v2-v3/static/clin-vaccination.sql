-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-vaccination.sql,v 1.2 2007-09-24 23:31:17 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.vaccination
	drop column fk_patient cascade;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-vaccination.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-vaccination.sql,v $
-- Revision 1.2  2007-09-24 23:31:17  ncq
-- - remove begin; commit; as it breaks the bootstrapper
--
-- Revision 1.1  2006/10/24 13:08:25  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
