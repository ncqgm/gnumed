-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table cfg.cfg_data
	add column pk serial;

alter table cfg.cfg_data
	add primary key (pk);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-cfg-cfg_data-static.sql', 'Revision: 1.1');
