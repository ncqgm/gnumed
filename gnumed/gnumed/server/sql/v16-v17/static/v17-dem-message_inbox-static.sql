-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .due_date
alter table dem.message_inbox
	add column due_date date;

alter table audit.log_message_inbox
	add column due_date date;


-- .expiry_date
alter table dem.message_inbox
	add column expiry_date date;

alter table audit.log_message_inbox
	add column expiry_date date;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-dem-message_inbox-static.sql', '17.0');
