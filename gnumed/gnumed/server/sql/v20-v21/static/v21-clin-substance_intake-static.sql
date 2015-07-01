-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.substance_intake add column comment_on_start text;

alter table audit.log_substance_intake add column comment_on_start text;

-- --------------------------------------------------------------
alter table clin.substance_intake add column harmful_use_type integer;

alter table audit.log_substance_intake add column harmful_use_type integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-substance_intake-static.sql', '21.0');
