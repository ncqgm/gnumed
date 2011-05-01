-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.generic_coding_system (
	pk serial primary key,
	code text,
	term text,
	fk_data_source integer
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-generic_coding_system-static.sql', '1.0');
