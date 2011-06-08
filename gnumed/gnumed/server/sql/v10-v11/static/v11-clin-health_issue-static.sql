-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-health_issue-static.sql,v 1.1 2009-04-07 13:09:33 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.health_issue
	add column
		grouping text
;


alter table audit.log_health_issue
	add column
		grouping text
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-health_issue-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-health_issue-static.sql,v $
-- Revision 1.1  2009-04-07 13:09:33  ncq
-- - new
--
--