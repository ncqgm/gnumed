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
-- .discontinued
alter table clin.substance_intake
	add column discontinued timestamp with time zone;

alter table audit.log_substance_intake
	add column discontinued timestamp with time zone;


-- .discontinue_reason
alter table clin.substance_intake
	add column discontinue_reason text;

alter table audit.log_substance_intake
	add column discontinue_reason text;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-clin-substance_intake-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
