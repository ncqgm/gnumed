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
create table ref.lnk_indic2vaccine (
	pk
		integer generated always as identity primary key,
	fk_indication
		integer,
	fk_vaccine
		integer
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-lnk_indic2vaccine-static.sql', '23.0');
