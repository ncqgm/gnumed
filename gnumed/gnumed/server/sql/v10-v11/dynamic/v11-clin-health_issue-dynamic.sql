-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-health_issue-dynamic.sql,v 1.1 2009-04-05 17:48:20 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.health_issue.grouping is
'This can be used to entirely arbitrarily group health
 issues felt to belong to each other.';


alter table clin.health_issue
	alter column grouping
		set default null
;


alter table clin.health_issue
	add constraint sane_grouping check (
		gm.is_null_or_non_empty_string(grouping)
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-health_issue-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-health_issue-dynamic.sql,v $
-- Revision 1.1  2009-04-05 17:48:20  ncq
-- - new
--
--