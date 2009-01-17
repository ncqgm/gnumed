-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-cfg-cfg_str_array.sql,v 1.2 2009-01-17 23:15:23 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmSoapPlugin","gmEMRJournalPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmMeasurementsGridPlugin","gmKOrganizerPlugin","gmDataMiningPlugin","gmXdtViewer","gmManual"}'
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
select gm.log_script_insertion('$RCSfile: v10-cfg-cfg_str_array.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-cfg-cfg_str_array.sql,v $
-- Revision 1.2  2009-01-17 23:15:23  ncq
-- - add waiting list to default workplace
--
-- Revision 1.1  2008/11/11 21:15:26  ncq
-- - add new soap plugin
--
--