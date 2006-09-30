-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - fix v_uniq_zipped_urbs
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: dem-v_uniq_zipped_urbs.sql,v 1.1 2006-09-30 10:33:00 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

grant select on dem.v_uniq_zipped_urbs to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-v_uniq_zipped_urbs.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-v_uniq_zipped_urbs.sql,v $
-- Revision 1.1  2006-09-30 10:33:00  ncq
-- - add missing grants
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
