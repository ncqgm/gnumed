-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v10-gm-access_log-static.sql,v 1.1 2008-12-12 16:33:40 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table gm.access_log (
	pk serial primary key,
	user_action text
		not null
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-gm-access_log-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-gm-access_log-static.sql,v $
-- Revision 1.1  2008-12-12 16:33:40  ncq
-- - HIPAA support
--
--