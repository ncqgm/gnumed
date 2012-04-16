-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
INSERT INTO dem.message_inbox (
	fk_staff,
	fk_inbox_item_type,
	comment,
	data
) VALUES (
	(select pk from dem.staff where db_user = 'any-doc'),
	(select pk_type from dem.v_inbox_item_type where type = 'memo' and category = 'administrative'),
	'Release Notes for GNUmed 1.2.rc1 (database v17.rc1)',
	'GNUmed 1.2.rc1 Release Notes:

	1.2.rc1

NEW: staff management: implement deletion
NEW: top panel: display active encounter area
NEW: patient overview plugin
NEW: reports to find recent encounters [thanks J.Busser]
NEW: marginal support for soapU category
NEW: placeholders form_name_long/form_name_short/form_version
NEW: document tree: sort mode "by health issue"
NEW: SimpleNotes plugin
NEW: current medication plugin: sort mode "by health issue"
NEW: AbiWord based document templates
NEW: document tree: add parts via document context menu
NEW: document tree: delete/move document parts via part context menu
NEW: browse reference data sources
NEW: importer for "Clinica" EMR databases
NEW: support estimated date of birth
NEW: placeholder <vaccination_history> and LaTeX form template
NEW: PDF-Formular "Vorsorgevollmacht" [thanks Bundesministerium f. Justiz]
NEW: active clinical reminders with due/expiry date
NEW: basic billing functionality

IMPROVED: EMR browser: whole-chart synopsis
IMPROVED: SOAP plugin: encounter field tooltips [thanks J.Busser]
IMPROVED: SOAP plugin: RFE/AOE fields only
IMPROVED: demographics: notebook tab order
IMPROVED: encounter list: [Add] uses configured default encounter type [thanks J.Busser]
IMPROVED: encounter list: [Start new], [Edit active], show active in red
IMPROVED: log data pack insertion in the database [thanks J.Busser]
IMPROVED: top panel: redo in wxGlade
IMPROVED: comm channels: support a comment [suggested by J.Busser]
IMPROVED: document input plugin: workflow adjustments
IMPROVED: signalling of attempt to duplicate drug component intake
IMPROVED: vaccinations: two-list item picker to pick indications rather than checkbox forest
IMPROVED: allergy manager workflow [thanks J.Busser]
IMPROVED: address related placeholders: let user select if no value available for type
IMPROVED: vaccinations: in EMR root show how long ago it was given
IMPROVED: waiting list: on activating patient set RFE if empty but waiting list has comment
IMPROVED: client upgrade check: version comparison glitch [thanks J.Busser]

	17.rc1

NEW: allow "*u*nspecified" in clin.clin_root_item/clin_narrative/soap_cat_ranks.soap_cat
NEW: i18n.untranslate()

IMPROVED: await <ENTER> before "exit 1" in bootstrap shell scripts [thanks Andreas]
IMRPOVED: gm.log_script_insertion() now logs script name in gm.access_log
IMPROVED: prevent active name from being deleted/deactivated at DB level
IMPROVED: constraints on i18n.translations
');

-- --------------------------------------------------------------
