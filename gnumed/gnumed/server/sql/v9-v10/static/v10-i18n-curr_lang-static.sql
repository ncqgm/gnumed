-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-i18n-curr_lang-static.sql,v 1.1 2008-10-26 01:20:30 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table i18n.curr_lang
	rename column "user" to db_user;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-i18n-curr_lang-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-i18n-curr_lang-static.sql,v $
-- Revision 1.1  2008-10-26 01:20:30  ncq
-- - "user" -> db_user
--
--