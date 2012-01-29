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
create table bill.bill (
	pk serial primary key,
	payment_method text,
	close_date timestamp with time zone,
	fk_receiver_identity integer,
	receiver_address text -- this is the address of the receiver of the bill, retrieved at close time
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-bill-static.sql', '17.0');
