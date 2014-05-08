-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.provider (
	pk serial primary key,
	fk_identity integer,
	fk_speciality integer
);

-- --------------------------------------------------------------
create table ref.provider_speciality (
	pk serial primary key,
	description text,
	icpcs text[]
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-ref-provider-static.sql', '20.0');
