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
update cfg.cfg_item set
	value = '["gmProviderInboxPlugin","gmWaitingListPlugin","gmPatientOverviewPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmCurrentSubstancesPlugin","gmMeasurementsGridPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmIncomingDataPlugin","gmExportAreaPlugin","gmEMRTimelinePlugin","gmPrintManagerPlugin","gmDataMiningPlugin","gmSimpleSoapPlugin","gmEMRJournalPlugin","gmBillingPlugin","gmKOrganizerPlugin","gmXdtViewer"]'::jsonb
where
	pk in (
		select pk_cfg_item
		from cfg.v_cfg_options
		where
			workplace = 'GNUmed Default'
			and option = 'horstspace.notebook.plugin_load_order'
		)
;

-- --------------------------------------------------------------
update cfg.cfg_item set
	value = '["gmProviderInboxPlugin","gmWaitingListPlugin","gmPatientOverviewPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmCurrentSubstancesPlugin","gmMeasurementsGridPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmIncomingDataPlugin","gmExportAreaPlugin","gmEMRTimelinePlugin","gmDataMiningPlugin","gmSimpleSoapPlugin","gmEMRJournalPlugin","gmBillingPlugin","gmPrintManagerPlugin"]'::jsonb
where
	pk in (
		select pk_cfg_item
		from cfg.v_cfg_options
		where
			workplace = 'Clinician'
			and option = 'horstspace.notebook.plugin_load_order'
		)
;

-- --------------------------------------------------------------
update cfg.cfg_item set
	value = '["gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmPrintManagerPlugin","gmScanIdxMedDocsPlugin","gmIncomingDataPlugin","gmExportAreaPlugin","gmKOrganizerPlugin"]'::jsonb
where
	pk in (
		select pk_cfg_item
		from cfg.v_cfg_options
		where
			workplace = 'Front Desk'
	 			and
			option = 'horstspace.notebook.plugin_load_order'
		)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-cfg-incoming_data_plugin.sql', '23.0');
