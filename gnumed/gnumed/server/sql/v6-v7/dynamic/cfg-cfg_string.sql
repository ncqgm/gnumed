-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: cfg-cfg_string.sql,v 1.1 2007-08-11 23:39:54 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.cfg_item where pk in (
	select pk_cfg_item from cfg.v_cfg_opts_string where option = 'horstspace.tmp_dir' and value like '%/gnumed/tmp%'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: cfg-cfg_string.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: cfg-cfg_string.sql,v $
-- Revision 1.1  2007-08-11 23:39:54  ncq
-- - fix tmp dir option
--
-- Revision 1.1  2007/07/09 11:11:48  ncq
-- - add KOrganizer plugin to default workplace
--
-- Revision 1.3  2007/04/20 08:26:10  ncq
-- - set default workplace to "GNUmed Default"
--
-- Revision 1.2  2007/04/06 23:19:31  ncq
-- - include data mining panel
--
-- Revision 1.1  2007/04/02 14:16:44  ncq
-- - added
--
--