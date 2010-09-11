-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.episode
	add column status text;


alter table audit.log_episode
	add column status text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-episode-static.sql', 'Revision: 1.1');
