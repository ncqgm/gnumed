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
create table clin.intake (
	pk
		integer generated always as identity primary key,
	use_type
		integer,
	fk_substance
		integer,
	notes4patient
		gm.nonempty_text,
	_fk_s_i
		integer
) inherits (clin.clin_root_item);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake-static.sql', '23.0');
