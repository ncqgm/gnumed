-- ===================================================
-- GnuMed default config data

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConfigData.sql,v $
-- $Revision: 1.2 $
-- ===================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- template
insert into cfg_template
	(name, type, description)
values (
	'plugin load order',
	'str_array',
	'which plugins to load in the GUI'
);

-- Arbeitsplatz Labor
insert into cfg_item
	(id_template, owner, workplace, cookie)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Labor',
	'gui'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmShowLab","gmLabJournal"}'
);

-- Arbeitsplatz (Dokumenten)archiv
insert into cfg_item
	(id_template, owner, workplace, cookie)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Archiv',
	'gui'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmShowMedDocs","gmIndexMedDocs","gmScanMedDocs"}'
);

-- Arbeitsplatz Sprechzimmer 1
insert into cfg_item
	(id_template, owner, workplace, cookie)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Sprechzimmer 1',
	'gui'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmShowLab","gmLabJournal","gmShowMedDocs","gmIndexMedDocs","gmScanMedDocs"}'
);

-- Arbeitsplatz Kinderarzt
insert into cfg_item
	(id_template, owner, workplace, cookie)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'Kinderarzt',
	'gui'
);

insert into cfg_str_array
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	'{"gmVaccinationsPlugin","gmShowMedDocs","gmShowLab"}'
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
delete from gm_schema_revision where filename='$RCSfile: gmConfigData.sql,v $');
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmConfigData.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmConfigData.sql,v $
-- Revision 1.2  2004-08-20 13:25:15  ncq
-- - add patient_search.always_dismiss_previous_patient
--
-- Revision 1.1  2004/07/19 14:41:55  ncq
-- - added some example workplaces
--
