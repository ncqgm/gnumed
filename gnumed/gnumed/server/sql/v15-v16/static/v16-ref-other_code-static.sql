-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.other_code (
	pk serial primary key
	--parent.code
	--parent.term
	--parent.comment
) inherits (ref.coding_system_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-other_code-static.sql', '16.0');
