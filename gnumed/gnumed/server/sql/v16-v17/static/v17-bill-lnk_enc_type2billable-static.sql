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
-- hm, should this be in ref. ?
create table bill.lnk_enc_type2billable (
	pk serial primary key,
	fk_encounter_type integer,
	fk_billable integer
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-bill-lnk_enc_type2billable-static.sql', '17.0');
