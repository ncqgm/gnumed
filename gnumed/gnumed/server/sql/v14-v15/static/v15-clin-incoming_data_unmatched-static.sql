-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .comment
alter table clin.incoming_data_unmatched
	add column comment text;

alter table audit.log_incoming_data_unmatched
	add column comment text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-incoming_data_unmatched-static.sql', 'Revision: 1.1');
