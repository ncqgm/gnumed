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
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmPatientOverviewPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmCurrentSubstancesPlugin","gmMeasurementsGridPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmEMRTimelinePlugin","gmKOrganizerPlugin","gmDataMiningPlugin","gmSimpleSoapPlugin","gmEMRJournalPlugin","gmBillingPlugin","gmXdtViewer"}'
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
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmPatientOverviewPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmCurrentSubstancesPlugin","gmMeasurementsGridPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmEMRTimelinePlugin","gmDataMiningPlugin","gmSimpleSoapPlugin","gmEMRJournalPlugin","gmBillingPlugin"}'
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
select gm.log_script_insertion('v18-cfg-cfg_str_array-dynamic.sql', '18.0');
