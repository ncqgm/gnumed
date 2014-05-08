-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.care_provider (
	pk serial primary key,
	fk_identity integer,
	fk_provider integer,
	comment text
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-care_provider-static.sql', '20.0');
