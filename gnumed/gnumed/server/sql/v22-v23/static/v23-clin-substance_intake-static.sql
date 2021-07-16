-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table clin.substance_intake
	add column fk_substance integer;

-- --------------------------------------------------------------
alter table clin.substance_intake
	add column fk_route integer;

alter table audit.log_substance_intake
	add column fk_route integer;

-- --------------------------------------------------------------
alter table clin.substance_intake
	add column fk_product integer;

alter table audit.log_substance_intake
	add column fk_product integer;

-- --------------------------------------------------------------
alter table clin.substance_intake
	add column notes_for_patient text;

alter table audit.log_substance_intake
	add column notes_for_patient text;

-- --------------------------------------------------------------
--alter table clin.substance_intake
--	drop column if exists fk_drug_component;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-substance_intake-static.sql', '23.0');
