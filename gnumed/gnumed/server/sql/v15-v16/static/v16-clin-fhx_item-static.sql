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
	rename to fhx_item;


alter table audit.log_hx_family_item
	rename to log_fhx_item;

-- --------------------------------------------------------------
alter table clin.fhx_item
	drop column fk_narrative_condition cascade;

alter table audit.log_fhx_item
	drop column fk_narrative_condition cascade;


alter table clin.fhx_item
	drop column fk_relative cascade;

alter table audit.log_fhx_item
	drop column fk_relative cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-fhx_item-static.sql', 'v16.0');
