-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - ...
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: zzz-template.sql,v 1.2 2006-09-16 21:47:37 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop ;
\set ON_ERROR_STOP 1



-- --------------------------------------------------------------
-- don't forget appropriate grants
grant  on  to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: zzz-template.sql,v $', '$Revision: 1.2 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: zzz-template.sql,v $
-- Revision 1.2  2006-09-16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
