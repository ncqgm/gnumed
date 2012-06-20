-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .reaction
alter table clin.vaccination
	add column reaction text;

alter table audit.log_vaccination
	add column reaction text;


-- .id -> .pk
alter table clin.vaccination
	rename column id to pk;

alter table audit.log_vaccination
	rename column id to pk;

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-vaccination-static.sql', 'Revision: 1.1');

