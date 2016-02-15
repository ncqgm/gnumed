-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmPatientOverviewPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmEMRListJournalPlugin","gmSoapPlugin","gmCurrentSubstancesPlugin","gmMeasurementsPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmPACSPlugin","gmExportAreaPlugin","gmEMRTimelinePlugin","gmPrintManagerPlugin","gmDataMiningPlugin","gmSimpleSoapPlugin","gmEMRJournalPlugin","gmBillingPlugin","gmKOrganizerPlugin","gmXdtViewer"}'
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
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmPatientOverviewPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmEMRListJournalPlugin","gmSoapPlugin","gmEMRListJournalPlugin","gmCurrentSubstancesPlugin","gmMeasurementsPlugin","gmShowMedDocs","gmPACSPlugin","gmScanIdxMedDocsPlugin","gmExportAreaPlugin","gmEMRTimelinePlugin","gmDataMiningPlugin","gmSimpleSoapPlugin","gmEMRJournalPlugin","gmBillingPlugin","gmPrintManagerPlugin"}'
where
	fk_item in (
		select pk_cfg_item
		from cfg.v_cfg_options
		where
			workplace = 'Clinician'
			and option = 'horstspace.notebook.plugin_load_order'
		)
;

-- --------------------------------------------------------------
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmPrintManagerPlugin","gmScanIdxMedDocsPlugin","gmExportAreaPlugin","gmKOrganizerPlugin"}'
where
	fk_item in (
		select pk_cfg_item
		from cfg.v_cfg_options
		where
			workplace = 'Front Desk'
	 			and
			option = 'horstspace.notebook.plugin_load_order'
		)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-cfg-cfg_str_array-dynamic.sql', '21.0');
