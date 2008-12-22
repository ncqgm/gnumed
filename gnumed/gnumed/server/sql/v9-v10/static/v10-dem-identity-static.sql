-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-dem-identity-static.sql,v 1.1 2008-12-22 18:53:44 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table dem.identity
	add column tob time without time zone;


alter table audit.log_identity
	add column tob time without time zone;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-dem-identity-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-dem-identity-static.sql,v $
-- Revision 1.1  2008-12-22 18:53:44  ncq
-- - add .tob
--
--