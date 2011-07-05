-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop table dem.lnk_identity2primary_doc cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-lnk_identity2primary_doc.sql', 'v16');
