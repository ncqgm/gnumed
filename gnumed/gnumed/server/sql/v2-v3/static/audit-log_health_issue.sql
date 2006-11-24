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
-- $Id: audit-log_health_issue.sql,v 1.1 2006-11-24 09:19:44 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table audit.log_health_issue
	rename column id_patient to fk_patient;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: audit-log_health_issue.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: audit-log_health_issue.sql,v $
-- Revision 1.1  2006-11-24 09:19:44  ncq
-- - need to alter col names on log tables, too, so audit triggers work
--
--