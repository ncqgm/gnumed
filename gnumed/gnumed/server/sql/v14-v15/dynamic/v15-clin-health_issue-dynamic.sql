-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.health_issue.summary is
'Used for tracking the summary of this health issue.';


alter table clin.health_issue
	add constraint health_issue_sane_summary check (
		gm.is_null_or_non_empty_string(summary)
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-health_issue-dynamic.sql', 'Revision: 1.1');
