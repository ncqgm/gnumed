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
	invoice_id text,
	close_date timestamp with time zone,
	apply_vat boolean,
	fk_receiver_identity integer,
	fk_receiver_address integer,
	fk_doc integer
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-bill-static.sql', '17.0');
