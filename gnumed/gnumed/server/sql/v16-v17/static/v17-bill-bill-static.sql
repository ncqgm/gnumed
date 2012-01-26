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
	-- NOT the receiver of the bill, the patient were invoicing for
	-- not needed because of bill.bill_item.fk_bill <-> bill.bill_item.fk_encounter -> .fk_patient
	--fk_identity integer,
	payment_method text,
	close_date timestamp with time zone,
	-- violates Single Source of Truth:
	--total_amount numeric(8,2), -- filled during close
	receiver_address text -- this is the address of the receiver of the bill, retrieved at close time
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-bill-static.sql', '17.0');
