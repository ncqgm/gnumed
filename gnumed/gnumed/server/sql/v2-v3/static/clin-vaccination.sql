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
-- $Id: clin-vaccination.sql,v 1.1 2006-10-24 13:08:25 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

alter table clin.vaccination
	drop column fk_patient cascade;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-vaccination.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: clin-vaccination.sql,v $
-- Revision 1.1  2006-10-24 13:08:25  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
