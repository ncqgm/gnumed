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
-- $Id: cfg-drop_old_tables.sql,v 1.1 2007-01-24 10:57:36 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop table cfg.db cascade;					-- drops cfg.config
drop table cfg.distributed_db cascade;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: cfg-drop_old_tables.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: cfg-drop_old_tables.sql,v $
-- Revision 1.1  2007-01-24 10:57:36  ncq
-- - eventually remove the old services related tables :-)
--
--
