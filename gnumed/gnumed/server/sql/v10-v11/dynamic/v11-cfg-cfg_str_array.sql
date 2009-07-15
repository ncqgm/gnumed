-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-cfg-cfg_str_array.sql,v 1.2 2009-07-15 12:26:39 ncq Exp $
-- $Revision: 1.2 $

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
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	(select pk from cfg.cfg_template where name = 'horstspace.notebook.plugin_load_order' and type = 'str_array'),
	'xxxDEFAULTxxx',
	'GNUmed Demo'
);


insert into cfg.cfg_str_array
	(fk_item, value)
values (
	(
	 select pk_cfg_item
	 from cfg.v_cfg_options
	 where
	 	workplace = 'GNUmed Demo'
	 		and
	 	option = 'horstspace.notebook.plugin_load_order'
	),
	'{"gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmMeasurementsGridPlugin","gmCurrentSubstancesPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmKOrganizerPlugin","gmDataMiningPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmXdtViewer"}'
);

-- --------------------------------------------------------------
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	(select pk from cfg.cfg_template where name = 'horstspace.notebook.plugin_load_order' and type = 'str_array'),
	'xxxDEFAULTxxx',
	'GNUmed Fallback'
);


insert into cfg.cfg_str_array
	(fk_item, value)
values (
	(
	 select pk_cfg_item
	 from cfg.v_cfg_options
	 where
	 	workplace = 'GNUmed Fallback'
	 		and
	 	option = 'horstspace.notebook.plugin_load_order'
	),
	'{"gmProviderInboxPlugin","gmDataMiningPlugin"}'
);


-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-cfg-cfg_str_array.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-cfg-cfg_str_array.sql,v $
-- Revision 1.2  2009-07-15 12:26:39  ncq
-- - add "GNUmed Demo" and "GNUmed Fallback"
--
--