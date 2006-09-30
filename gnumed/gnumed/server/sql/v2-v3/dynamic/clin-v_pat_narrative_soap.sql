-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - fix v_pat_narrative_soap
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: clin-v_pat_narrative_soap.sql,v 1.1 2006-09-30 10:33:01 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

grant select on clin.v_pat_narrative_soap to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-v_pat_narrative_soap.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-v_pat_narrative_soap.sql,v $
-- Revision 1.1  2006-09-30 10:33:01  ncq
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
