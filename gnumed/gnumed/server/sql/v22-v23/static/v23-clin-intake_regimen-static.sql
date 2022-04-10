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
create table clin.intake_regimen (
	pk integer generated always as identity primary key,
	fk_intake
		integer,
	fk_dose
		integer,
	--fk_drug_component
	--	integer,
	fk_drug_product
		integer,
	--.narrative:
	--schedule
	--	gm.nonempty_text,
	--.clin_when:
	--started
	--	timestamp with time zone,
	comment_on_start
		gm.nonempty_text,
	discontinued
		timestamp with time zone,
	discontinue_reason
		gm.nonempty_text,
	planned_duration
		interval
) inherits (clin.clin_root_item);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake_regimen-static.sql', '23.0');
