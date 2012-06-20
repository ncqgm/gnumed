-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-dem-message_inbox-static.sql,v 1.1 2009-08-28 12:43:04 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table dem.provider_inbox
	rename to message_inbox;

alter table audit.log_provider_inbox
	rename to log_message_inbox;



alter table dem.message_inbox
	add column fk_patient integer
		default null
		references dem.identity(pk)
		on update cascade
		on delete restrict
;

alter table audit.log_message_inbox
	add column fk_patient integer
;


-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-dem-message_inbox-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-dem-message_inbox-static.sql,v $
-- Revision 1.1  2009-08-28 12:43:04  ncq
-- - rename to message inbox
-- - add fk_patient
--
--
