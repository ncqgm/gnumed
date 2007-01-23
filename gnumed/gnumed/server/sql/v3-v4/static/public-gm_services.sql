-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: public-gm_services.sql,v 1.2 2007-01-23 14:00:45 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop table public.gm_services cascade;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: public-gm_services.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: public-gm_services.sql,v $
-- Revision 1.2  2007-01-23 14:00:45  ncq
-- - backport from 0.2.4
--
-- Revision 1.1.2.1  2007/01/23 13:52:30  ncq
-- - no need for this table anymore
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
