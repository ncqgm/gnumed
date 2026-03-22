-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: 
-- 
-- ==============================================================
drop index if exists clin.idx_narrative_modified_by;

create index idx_narrative_modified_by on clin.clin_narrative(modified_by);

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-clin_narrative.sql,v $', '$Revision: 1.1 $');
