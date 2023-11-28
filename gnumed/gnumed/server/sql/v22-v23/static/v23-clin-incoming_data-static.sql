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
alter table clin.incoming_data_unmatched
	rename column fk_identity_disambiguated to fk_identity;

alter table clin.incoming_data_unmatched
	rename to incoming_data;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-incoming_data-static.sql', '23.0');
