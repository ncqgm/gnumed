-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.coda (
	pk serial primary key,
	--parent.code = icd10
	--parent.term = Beratungsanlass
	--parent.comment
	icd10_text text
) inherits (ref.coding_system_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-coda-static.sql', '18.0');
