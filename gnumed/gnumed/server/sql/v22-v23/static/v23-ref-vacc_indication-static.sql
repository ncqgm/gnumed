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
create table ref.vacc_indication (
	pk
		integer generated always as identity primary key,
	target
		gm.nonempty_text,
	atc
		gm.nonempty_text
);

alter table audit.log_vacc_indication
	add column pk integer;

alter table audit.log_vacc_indication
	add column target text;

alter table audit.log_vacc_indication
	add column atc text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-vacc_indication-static.sql', '23.0');
