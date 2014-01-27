-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table gm.notifying_tables drop column signal cascade;
alter table gm.notifying_tables drop column carries_identity_pk cascade;

--unique_entry

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-gm-notifying_tables-static.sql', '20.0');
