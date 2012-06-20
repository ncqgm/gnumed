-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v12-cfg-cfg_str_array-dynamic.sql,v 1.1 2009-10-28 16:45:08 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmCurrentSubstancesPlugin","gmMeasurementsGridPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmKOrganizerPlugin","gmDataMiningPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmXdtViewer"}'
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
delete from cfg.cfg_item
where
	fk_template = (select pk from cfg.cfg_template where name = 'horstspace.notebook.plugin_load_order' and type = 'str_array')
		and
	workplace = 'Front Desk'
;


insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	(select pk from cfg.cfg_template where name = 'horstspace.notebook.plugin_load_order' and type = 'str_array'),
	'xxxDEFAULTxxx',
	'Front Desk'
);


insert into cfg.cfg_str_array
	(fk_item, value)
values (
	(
	 select pk_cfg_item
	 from cfg.v_cfg_options
	 where
	 	workplace = 'Front Desk'
	 		and
	 	option = 'horstspace.notebook.plugin_load_order'
	),
	'{"gmProviderInboxPlugin","gmKOrganizerPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmScanIdxMedDocsPlugin"}'
);


-- --------------------------------------------------------------
delete from cfg.cfg_item
where
	fk_template = (select pk from cfg.cfg_template where name = 'horstspace.notebook.plugin_load_order' and type = 'str_array')
		and
	workplace = 'Clinician'
;


insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	(select pk from cfg.cfg_template where name = 'horstspace.notebook.plugin_load_order' and type = 'str_array'),
	'xxxDEFAULTxxx',
	'Clinician'
);


insert into cfg.cfg_str_array
	(fk_item, value)
values (
	(
	 select pk_cfg_item
	 from cfg.v_cfg_options
	 where
	 	workplace = 'Clinician'
	 		and
	 	option = 'horstspace.notebook.plugin_load_order'
	),
	'{"gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmCurrentSubstancesPlugin","gmMeasurementsGridPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmDataMiningPlugin","gmEMRJournalPlugin"}'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-cfg-cfg_str_array-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-cfg-cfg_str_array-dynamic.sql,v $
-- Revision 1.1  2009-10-28 16:45:08  ncq
-- - include Substance intake plugin
--
--