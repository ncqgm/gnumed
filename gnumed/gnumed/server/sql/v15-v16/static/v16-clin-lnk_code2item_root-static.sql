-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.lnk_code2item_root (
	pk_lnk_code2item serial primary key,
	fk_generic_code integer,
	fk_item integer
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2item_root-static.sql', '1.0');
