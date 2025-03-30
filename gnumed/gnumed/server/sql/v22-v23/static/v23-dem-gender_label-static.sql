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
alter table dem.gender_label
	add column symbol text;


alter table audit.log_gender_label
	add column symbol text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-gender_label-static.sql', '23.0');
