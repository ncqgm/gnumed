-- ===================================================
-- GnuMed default config data

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConfigData.sql,v $
-- $Revision: 1.21 $
-- ===================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================
INSERT INTO cfg.distributed_db(name) values('default');
INSERT INTO cfg.distributed_db(name) values('personalia');
INSERT INTO cfg.distributed_db(name) values('historica');
INSERT INTO cfg.distributed_db(name) values('pharmaceutica');
INSERT INTO cfg.distributed_db(name) values('reference');
INSERT INTO cfg.distributed_db(name) values('blobs');
insert into cfg.distributed_db(name) values('administrivia');

-- =============================================
INSERT INTO cfg.cfg_type_enum VALUES ('string');
INSERT INTO cfg.cfg_type_enum VALUES ('numeric');
INSERT INTO cfg.cfg_type_enum VALUES ('str_array');
insert into cfg.cfg_type_enum values ('data');

-- =============================================
-- template
insert into cfg.cfg_template
	(name, type, description)
values (
	'horstspace.notebook.plugin_load_order',
	'str_array',
	'which plugins to load in the GUI'
);

-- a 'workplace' called "Librarian (0.2)"
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'Librarian Release (0.2)'
);

insert into cfg.cfg_str_array
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	'{"gmManual","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmConfigRegistry"}'
);

-- Arbeitsplatz Labor
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'Labor'
);

insert into cfg.cfg_str_array
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	'{"gmShowLab","gmLabJournal","gmConfigRegistry"}'
);

-- Arbeitsplatz (Dokumenten)archiv
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'Dokumente'
);

insert into cfg.cfg_str_array
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	'{"gmShowMedDocs","gmIndexMedDocs","gmScanMedDocs","gmConfigRegistry"}'
);

-- Arbeitsplatz Sprechzimmer 1
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'Sprechzimmer 1'
);

insert into cfg.cfg_str_array
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	'{"gmShowLab","gmLabJournal","gmShowMedDocs","gmIndexMedDocs","gmScanMedDocs","gmConfigRegistry"}'
);

-- Arbeitsplatz Kinderarzt
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'Kinderarzt'
);

insert into cfg.cfg_str_array
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	'{"gmVaccinationsPlugin","gmShowMedDocs","gmShowLab","gmConfigRegistry"}'
);

-- Arbeitsplatz Archivbrowser
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'Archivbrowser'
);

insert into cfg.cfg_str_array
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	'{"gmOffice","gmShowMedDocs","gmShowLab","gmLabJournal","gmVaccinationsPlugin","gmAllergiesPlugin","gmConfigRegistry"}'
);

-- Arbeitsplatz Impfbrowser
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'Impfungen'
);

insert into cfg.cfg_str_array
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	'{"gmVaccinationsPlugin","gmConfigRegistry"}'
);


-- ---------------------------------------------
-- search behaviour options

-- dismiss or keep previously active patient
insert into cfg.cfg_template
	(name, type, description)
values (
	'patient_search.always_dismiss_previous_patient',
	'numeric',
	'1/0, meaning true/false,
	 if true: dismiss previous patient regardless of search result,
	 if false: keep previous patient active if no new patient found'
);

insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'xxxDEFAULTxxx'
);

-- default to false as code hasn't been verified for true
insert into cfg.cfg_numeric
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	0
);

-- reload patient data after search even if same patient
insert into cfg.cfg_template
	(name, type, description)
values (
	'patient_search.always_reload_new_patient',
	'numeric',
	'1/0, meaning true/false,
	 if true: reload patient data after search even if the new patient is the same as the previous one,
	 if false: do not reload data if new patient matches previous one'
);

insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'xxxDEFAULTxxx'
);

-- default to false
insert into cfg.cfg_numeric
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	0
);

-- scan & index behaviour options ------------------------------
-- show document ID after import
insert into cfg.cfg_template
	(name, type, description)
values (
	'horstspace.scan_index.show_doc_id',
	'boolean',
	'1/0, meaning true/false,
	 True: after importing a new document display the document ID,
	 False: do not display the document ID for a new document after import'
);

insert into cfg.cfg_item
	(fk_template, owner)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx'
);

-- default to True
insert into cfg.cfg_numeric
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	1
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmConfigData.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmConfigData.sql,v $', '$Revision: 1.21 $');

-- =============================================
-- $Log: gmConfigData.sql,v $
-- Revision 1.21  2005-12-14 10:43:33  ncq
-- - add option on showing document ID after import
-- - several clin.clin_* -> clin.* renames
--
-- Revision 1.20  2005/11/27 12:59:56  ncq
-- - add ScanIdxMedDocsPlugin to Librarian 0.2 release config
--
-- Revision 1.19  2005/11/18 15:41:45  ncq
-- - add data from gmconfiguration.sql
-- - adjust for cfg.* schema usage
-- - remove stale KnoppixMedica workplace
--
-- Revision 1.18  2005/11/01 08:53:25  ncq
-- - add document viewer to 0.2 workplace plugin config
--
-- Revision 1.17  2005/10/30 21:37:07  ncq
-- - add "Librarian Release (0.2)" config
--
-- Revision 1.16  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.15  2005/09/11 17:44:02  ncq
-- - add patient_search.always_reload_new_patient option
--
-- Revision 1.14  2005/07/14 21:31:42  ncq
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
