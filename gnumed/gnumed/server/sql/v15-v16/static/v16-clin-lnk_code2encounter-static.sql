-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.lnk_code2rfe (
	pk serial primary key
) inherits (clin.lnk_code2item_root);

-- --------------------------------------------------------------
create table clin.lnk_code2aoe (
	pk serial primary key
) inherits (clin.lnk_code2item_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2encounter-static.sql', '1.0');
