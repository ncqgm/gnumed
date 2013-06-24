-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table dem.lnk_org_unit2comm
	add column comment text;

alter table audit.log_lnk_org_unit2comm
	add column comment text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-lnk_org_unit2comm-static.sql', '19.0');
