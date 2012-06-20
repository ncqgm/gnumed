-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_message_inbox cascade;
\set ON_ERROR_STOP 1

-- .ufk_context
alter table dem.message_inbox
	add column ufk_context_array integer[];

alter table audit.log_message_inbox
	add column ufk_context_array integer[];

update dem.message_inbox set
	ufk_context_array = ARRAY[ufk_context];

alter table dem.message_inbox
	drop column ufk_context;

alter table dem.message_inbox
	rename column ufk_context_array to ufk_context;

alter table audit.log_message_inbox
	drop column ufk_context;

-- .importance
alter table dem.message_inbox
	alter column importance
		set not null;


alter table audit.log_message_inbox
	rename column ufk_context_array to ufk_context;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-identity-static.sql', 'Revision: 1.1');
