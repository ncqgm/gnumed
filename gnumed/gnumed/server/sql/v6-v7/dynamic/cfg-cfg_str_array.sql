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
-- $Id: cfg-cfg_str_array.sql,v 1.1 2007-07-09 11:11:48 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmKOrganizerPlugin","gmDataMiningPlugin","gmXdtViewer","gmManual","gmConfigRegistry"}'
where
	fk_item in (select pk_cfg_item from cfg.v_cfg_options where workplace = 'GNUmed Default' and option = 'horstspace.notebook.plugin_load_order')
;
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: cfg-cfg_str_array.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: cfg-cfg_str_array.sql,v $
-- Revision 1.1  2007-07-09 11:11:48  ncq
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