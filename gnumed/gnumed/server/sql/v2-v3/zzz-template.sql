-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: zzz-template.sql,v 1.5 2006-10-24 13:09:45 ncq Exp $
-- $Revision: 1.5 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop forgot_to_edit_drops;
\set ON_ERROR_STOP 1


comment on forgot_to_edit_comment is
	'';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: zzz-template.sql,v $', '$Revision: 1.5 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: zzz-template.sql,v $
-- Revision 1.5  2006-10-24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
