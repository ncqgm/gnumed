-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table if exists ref.loinc_staging set schema staging;

-- ==============================================================
select gm.log_script_insertion('v20-ref-loinc_staging-dynamic.sql', '20.0');
