-- ===================================================
-- GnuMed default config data

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConfigData.sql,v $
-- $Revision: 1.14 $
-- ===================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- template
insert into cfg_template
	(name, type, description)
values (
	'horstspace.notebook.plugin_load_order',
	'str_array',
	'which plugins to load in the GUI'
);

-- a 'workplace' called "Release 0.1"
insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Release 0.1'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmManual","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmConfigRegistry"}'
);

-- Arbeitsplatz Labor
insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Labor'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmShowLab","gmLabJournal","gmConfigRegistry"}'
);

-- Arbeitsplatz (Dokumenten)archiv
insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Dokumente'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmShowMedDocs","gmIndexMedDocs","gmScanMedDocs","gmConfigRegistry"}'
);

-- Arbeitsplatz Sprechzimmer 1
insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Sprechzimmer 1'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmShowLab","gmLabJournal","gmShowMedDocs","gmIndexMedDocs","gmScanMedDocs","gmConfigRegistry"}'
);

-- Arbeitsplatz Kinderarzt
insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Kinderarzt'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmVaccinationsPlugin","gmShowMedDocs","gmShowLab","gmConfigRegistry"}'
);

-- Arbeitsplatz Archivbrowser
insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Archivbrowser'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmOffice","gmShowMedDocs","gmShowLab","gmLabJournal","gmVaccinationsPlugin","gmAllergiesPlugin","gmConfigRegistry"}'
);

-- Arbeitsplatz KnoppixMedica CD-Nutzer
insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'KnoppixMedica'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmOffice","gmShowMedDocs","gmShowLab","gmLabJournal","gmVaccinationsPlugin","gmAllergiesPlugin","gmConfigRegistry","gmEMRBrowserPlugin","gmEMRTextDumpPlugin","gmSingleBoxSoapPlugin","gmStikoBrowser","gmXdtViewer","gmManual","gmDemographicsEditor"}'
);

-- Arbeitsplatz Impfbrowser
insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Impfungen'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmVaccinationsPlugin","gmConfigRegistry"}'
);


-- ---------------------------------------------
-- search behaviour options

-- dismiss or keep previously active patient
insert into cfg_template
	(name, type, description)
values (
	'patient_search.always_dismiss_previous_patient',
	'numeric',
	'1/0, meaning true/false,
	 if true: dismiss previous patient regardless of search result,
	 if false: keep previous patient active if no new patient found'
);

insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'xxxDEFAULTxxx'
);

-- default to false as code hasn't been verified for true
insert into cfg_numeric
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	0
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmConfigData.sql,v $';
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmConfigData.sql,v $', '$Revision: 1.14 $', False);

-- =============================================
-- $Log: gmConfigData.sql,v $
-- Revision 1.14  2005-07-14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.13  2005/05/30 09:14:52  ncq
-- - make notebooked patient editor the default
--
-- Revision 1.12  2005/05/24 19:58:39  ncq
-- - favour notebook over sash for progress note input, the
--   code is more maintainable
--
-- Revision 1.11  2005/05/08 21:51:20  ncq
-- - add notebooked progress note editor to Release 0.1 config
--
-- Revision 1.10  2005/04/12 16:35:42  ncq
-- - add journal as alternative view for EMR
--
-- Revision 1.9  2005/04/02 22:32:50  ncq
-- - move closer to compliance with 0.1 roadmap
--
-- Revision 1.8  2005/03/20 18:08:37  ncq
-- - add multisashed progress note input to "Release 0.1" as notebook plugin
--
-- Revision 1.7  2005/03/08 13:33:35  ncq
-- - added workplace "Release 0.1"
--
-- Revision 1.6  2005/01/09 19:49:39  ncq
-- - add vaccination browser workplace definition
--
-- Revision 1.5  2004/10/19 22:18:34  sjtan
-- fix syntax error end bracket.
--
-- Revision 1.4  2004/10/01 13:26:15  ncq
-- - add workplace "KnoppixMedica" CD user
--
-- Revision 1.3  2004/09/13 19:25:56  ncq
-- - "plugin load order" with cookie "gui" now "horstspace.notebook.plugin_load_order"
--
-- Revision 1.2  2004/08/20 13:25:15  ncq
-- - add patient_search.always_dismiss_previous_patient
--
-- Revision 1.1  2004/07/19 14:41:55  ncq
-- - added some example workplaces
--
