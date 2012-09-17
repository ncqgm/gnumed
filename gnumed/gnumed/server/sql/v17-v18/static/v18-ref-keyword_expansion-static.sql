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
alter table clin.keyword_expansion
	set schema ref;


alter table ref.keyword_expansion
	add column encrypted boolean
		default false;


alter table ref.keyword_expansion
	add column binary_data bytea;


alter table ref.keyword_expansion
	rename column expansion to textual_data;

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-keyword_expansion-static.sql', '18.0');
