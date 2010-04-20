-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
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

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-vaccination-static.sql', 'Revision: 1.1');

