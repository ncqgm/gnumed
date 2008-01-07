-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-dem-lnk_identity2comm.sql,v 1.1 2008-01-07 17:08:47 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
update dem.lnk_identity2comm set fk_type = 1 where fk_type is NULL;

alter table dem.lnk_identity2comm
	alter column fk_type set not NULL;


delete from dem.lnk_identity2comm where url is NULL;

alter table dem.lnk_identity2comm
	alter column url set not NULL;


delete from dem.lnk_identity2comm where trim(url) = '';

alter table dem.lnk_identity2comm
	add check (trim(url) <> '');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-dem-lnk_identity2comm.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-dem-lnk_identity2comm.sql,v $
-- Revision 1.1  2008-01-07 17:08:47  ncq
-- - adjust column constraints
--
--