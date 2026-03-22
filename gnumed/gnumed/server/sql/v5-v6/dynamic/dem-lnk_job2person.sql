-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
grant select, insert, update, delete on dem.lnk_job2person to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: dem-lnk_job2person.sql,v $', '$Revision: 1.1 $');
