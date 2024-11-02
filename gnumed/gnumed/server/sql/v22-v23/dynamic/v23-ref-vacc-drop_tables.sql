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
drop table if exists ref.vacc_route cascade;

delete from audit.audited_tables where schema = 'ref' and table_name = 'vacc_route';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-vacc-drop_tables.sql', '23.0');
