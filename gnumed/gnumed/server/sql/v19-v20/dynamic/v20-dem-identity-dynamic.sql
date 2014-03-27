-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table dem.identity
	drop column if exists karyotype cascade;

alter table audit.log_identity
	drop column if exists karyotype cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-dem-identity-dynamic.sql', '20.0');
