-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.hx_family_item
	add column fk_condition_issue integer;

alter table clin.hx_family_item
	add column fk_condition_episode integer;

alter table clin.hx_family_item
	drop column fk_narrative_condition cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-hx_family_item-static.sql', 'Revision: 1.1');
