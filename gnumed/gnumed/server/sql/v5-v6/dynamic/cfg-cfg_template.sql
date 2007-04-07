-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: cfg-cfg_template.sql,v 1.1 2007-04-07 22:30:36 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.cfg_template where name = 'patient_activation.script_to_run_after_activation';

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: cfg-cfg_template.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: cfg-cfg_template.sql,v $
-- Revision 1.1  2007-04-07 22:30:36  ncq
-- - factored out dynamic part
--
-- Revision 1.1  2007/04/02 14:16:44  ncq
-- - added
--
--