-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .context
alter table dem.enum_ext_id_types
	drop column context cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-enum_ext_id_types-static.sql', 'Revision: 1.1');
