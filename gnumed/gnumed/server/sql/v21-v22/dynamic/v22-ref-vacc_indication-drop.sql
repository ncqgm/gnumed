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
drop table if exists ref.lnk_vaccine2inds cascade;
delete from audit.audited_tables where
	schema = 'ref'
		and
	table_name = 'lnk_vaccine2inds';

-- --------------------------------------------------------------
drop table if exists ref.vacc_indication cascade;
delete from audit.audited_tables where
	schema = 'ref'
		and
	table_name = 'vacc_indication';

-- --------------------------------------------------------------
-- new-style vaccines are not linked to indications, so drop
-- trigger asserting that condition,
-- it had already been disabled for creation of new vaccines
drop function if exists clin.trf_sanity_check_vaccine_has_indications() cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-vacc_indication-drop.sql', '22.0');
