-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.register_notifying_table('dem', 'lnk_job2person', 'job');

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-dem-lnk_job2person-dynamic.sql', '17.0');
