-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.icd10 (
	pk serial primary key,
	--parent.code
	--parent.term
	--parent.comment
	star_code text,
	aux_code text
) inherits (ref.coding_system_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-icd10-static.sql', '16.0');
