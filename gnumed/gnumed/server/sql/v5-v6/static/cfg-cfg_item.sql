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
-- $Id: cfg-cfg_item.sql,v 1.2 2007-04-20 08:26:10 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	(select pk from cfg.cfg_template where name='horstspace.notebook.plugin_load_order' and type='str_array'),
	'xxxDEFAULTxxx',
	'GNUmed Default'
);

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: cfg-cfg_item.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: cfg-cfg_item.sql,v $
-- Revision 1.2  2007-04-20 08:26:10  ncq
-- - set default workplace to "GNUmed Default"
--
-- Revision 1.1  2007/04/02 14:16:44  ncq
-- - added
--
--