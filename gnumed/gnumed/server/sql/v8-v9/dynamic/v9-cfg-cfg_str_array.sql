-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-cfg-cfg_str_array.sql,v 1.1 2008-01-07 20:49:52 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmKOrganizerPlugin","gmDataMiningPlugin","gmXdtViewer","gmManual"}'
where
	fk_item in (select pk_cfg_item from cfg.v_cfg_options where workplace = 'GNUmed Default' and option = 'horstspace.notebook.plugin_load_order')
;
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-cfg-cfg_str_array.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-cfg-cfg_str_array.sql,v $
-- Revision 1.1  2008-01-07 20:49:52  ncq
-- - remove ConfigRegistry
--
--