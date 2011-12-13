-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table dem.lnk_identity2comm
	add column comment text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-dem-lnk_identity2comm-static.sql', '17.0');
