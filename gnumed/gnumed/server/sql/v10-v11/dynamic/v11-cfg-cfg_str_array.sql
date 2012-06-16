-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-cfg-cfg_str_array.sql,v 1.5 2009-08-13 12:19:41 ncq Exp $
-- $Revision: 1.5 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- ,"gmCurrentSubstancesPlugin"
update cfg.cfg_str_array set
	value = '{"gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmMeasurementsGridPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmKOrganizerPlugin","gmDataMiningPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmXdtViewer"}'
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


-- ,"gmCurrentSubstancesPlugin"
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
	'{"gmProviderInboxPlugin","gmWaitingListPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmSoapPlugin","gmMeasurementsGridPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmDataMiningPlugin","gmEMRJournalPlugin"}'
);

-- --------------------------------------------------------------
-- delete old workplaces
delete from cfg.cfg_item
where
	fk_template = (
		select pk
		from cfg.cfg_template
		where name = 'horstspace.notebook.plugin_load_order'
	)
		and
	workplace in (
		'post-Librarian Release (0.3)',
		'Librarian Release (0.2)',
		'Labor',
		'Dokumente',
		'Sprechzimmer 1',
		'Kinderarzt',
		'Archivbrowser',
		'Impfungen',
		'Release 0.2.3',
		'Release 0.2.4',
		'Release 0.2.5'
	)
;

delete from cfg.cfg_item
where
	workplace in
		'post-Librarian Release (0.3)',
		'Librarian Release (0.2)',
		'Labor',
		'Dokumente',
		'Sprechzimmer 1',
		'Kinderarzt',
		'Archivbrowser',
		'Impfungen',
		'Release 0.2.3',
		'Release 0.2.4',
		'Release 0.2.5'
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-cfg-cfg_str_array.sql,v $', '$Revision: 1.5 $');

-- ==============================================================
-- $Log: v11-cfg-cfg_str_array.sql,v $
-- Revision 1.5  2009-08-13 12:19:41  ncq
-- - remove current substances plugin as it does not usefully
--   do anything yet
--
-- Revision 1.4  2009/08/03 20:52:57  ncq
-- - set workplaces as per list discussion
--
-- Revision 1.3  2009/07/23 20:05:31  ncq
-- - adjust workplaces as per list discussion
--
-- Revision 1.2  2009/07/15 12:26:39  ncq
-- - add "GNUmed Demo" and "GNUmed Fallback"
--
--