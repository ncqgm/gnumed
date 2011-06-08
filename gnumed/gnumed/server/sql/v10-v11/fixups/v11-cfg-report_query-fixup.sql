-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-cfg-report_query-fixup.sql,v 1.1 2010-01-01 21:18:39 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
update cfg.report_query
set
	label = 'patients whose narrative contains a certain coded term'
where
	label = 'patients whose narrative constains a certain coded term'
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-cfg-report_query-fixup.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-cfg-report_query-fixup.sql,v $
-- Revision 1.1  2010-01-01 21:18:39  ncq
-- - fix typo
--
--