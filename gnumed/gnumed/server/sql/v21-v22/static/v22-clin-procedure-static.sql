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
alter table clin.procedure
	add column fk_doc integer;

alter table audit.log_procedure
	add column fk_doc integer;


alter table clin.procedure
	add column comment text;

alter table audit.log_procedure
	add column comment text;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-procedure-static.sql', '22.0');
