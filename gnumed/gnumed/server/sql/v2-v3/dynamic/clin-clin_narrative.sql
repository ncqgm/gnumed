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
-- $Id: clin-clin_narrative.sql,v 1.1 2006-12-11 16:59:47 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_narrative_modified_by;
\set ON_ERROR_STOP 1

create index idx_narrative_modified_by on clin.clin_narrative(modified_by);

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-clin_narrative.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-clin_narrative.sql,v $
-- Revision 1.1  2006-12-11 16:59:47  ncq
-- - use dem.v_staff -> dem.staff in provider resolution
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
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
