-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.incoming_data_unmatched
	add column fk_provider_disambiguated integer;


alter table audit.log_incoming_data_unmatched
	add column fk_provider_disambiguated integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-incoming_data_unmatched-static.sql', '16.0');
