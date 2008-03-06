-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-lab_request-static.sql,v 1.2 2008-03-06 23:21:38 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.lab_request
	add column diagnostic_service_section text;

alter table clin.lab_request
	add column ordered_service text;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-lab_request-static.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v9-clin-lab_request-static.sql,v $
-- Revision 1.2  2008-03-06 23:21:38  ncq
-- - audit table doesn't exist yet
--
-- Revision 1.1  2008/03/05 22:36:11  ncq
-- - new
--
-- Revision 1.1  2008/03/02 11:25:01  ncq
-- - new files
