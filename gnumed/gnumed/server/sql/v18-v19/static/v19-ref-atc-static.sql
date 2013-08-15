-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table ref.atc
	drop column ddd cascade;

alter table ref.atc
	drop column unit cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-ref-atc-static.sql', '19.0');
