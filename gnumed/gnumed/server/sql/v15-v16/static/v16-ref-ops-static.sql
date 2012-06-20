-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.ops (
	pk serial primary key,
	second_code text,
	requires_laterality boolean
	--parent.code
	--parent.term
	--parent.comment
) inherits (ref.coding_system_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-ops-static.sql', '16.0');
