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
alter table bill.bill
	add column comment text;


alter table audit.log_bill
	add column comment text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-bill-bill-static.sql', '18.0');
