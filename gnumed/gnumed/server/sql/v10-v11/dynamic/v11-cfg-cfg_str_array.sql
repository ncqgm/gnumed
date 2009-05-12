-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-cfg-cfg_str_array.sql,v 1.1 2009-05-12 12:01:12 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmMeasurementsGridPlugin","gmCurrentSubstancesPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmKOrganizerPlugin","gmDataMiningPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmXdtViewer"}'
where
	fk_item in (
		select pk_cfg_item
		from cfg.v_cfg_options
		where
			workplace = 'GNUmed Default'
			and option = 'horstspace.notebook.plugin_load_order'
		)
;
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-cfg-cfg_str_array.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-cfg-cfg_str_array.sql,v $
-- Revision 1.1  2009-05-12 12:01:12  ncq
-- - include medication plugin
--
--