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
create table ref.billable (
	pk serial primary key,
	fk_data_source integer,
	amount numeric,
	currency text,
	vat_multiplier numeric,			-- does this *really* belong here ?
	active boolean,
	discountable boolean
) inherits (ref.coding_system_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-billable-static.sql', '17.0');
