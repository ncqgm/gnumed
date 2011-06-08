-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on function gm.is_null_or_blank_string(text) is
'input is either NULL or empty string -> True; 
input is not NULL and not empty -> FALSE';


-- fix empty string issue lateralities
update clin.health_issue set
	laterality = gm.nullify_empty_string(laterality)
where
	gm.is_null_or_blank_string(laterality) is True
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-clin_narrative-dynamic.sql', 'Revision: 1.1');

