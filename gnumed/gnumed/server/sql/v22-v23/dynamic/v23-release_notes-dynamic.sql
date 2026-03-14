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
	'Release Notes for GNUmed 1.9.0 (database v23.0)',
	'GNUmed 1.9.0 Release Notes:

	1.9.0

NEW: tool: generate_man_page
NEW: placeholder: $yes_no$
NEW: lists: persistent item selection across sorts/reloads
NEW: lists: Drag&Drop support
NEW: paperwork: write non-templated letter w/ LibreOffice
NEW: export area: join items into one PDF
NEW: debug: database owner connection test menu item
NEW: login: focus previously used praxis branch
NEW: file describer: include pdffonts
NEW: export area: escrow passphrases used during file export
NEW: tool: get_object_passphrases
NEW: plugins: gmIncomingAreaPlugin supercedes gmScanIdxMedDocsPlugin
NEW: tool: update_collations
NEW: forms: failsafe medication list
NEW: forms: failsafe vaccination history
NEW: forms: failsafe lab results list
NEW: documents: failsafe documents list
NEW: paperwork: direct access to failsafe forms
NEW: forms: failsafe progress notes form
NEW: macro expansions in LaTeX templates
NEW: demographics: editable gender definitions
NEW: demographics: add auxiliary information on identity
NEW: remove explicit gm-fingerprint_db.py
NEW: run --tool=fingerprint_db if started as gm-fingerprint_db(.py)

IMPROVED: GUI: show current patient/provider in window titles
IMPROVED: placeholder: $current_provider_name$
IMPROVED: forms: LaTeX: 5 instead of 3 placeholder parsing passes
IMPROVED: forms: LaTeX template templates
IMPROVED: hooks: example script template
IMPROVED: startup: git branch detection
IMPROVED: bills: invoice ID locking
IMPROVED: M/VCF: add nominatim URL to patient/praxis MECARD/vCard
IMPROVED: files: format conversion improvements
IMPROVED: DB: replace "IN"/"NOT IN" for psycopg3
IMPROVED: DB: converge localhost/domain socket profiles
IMPROVED: export area: support D&D of items as files
IMPROVED: search: use clin.v_narrative4search again
IMPROVED: test results: multi-test plotting [thanks brulefa]
IMPROVED: code: configuration handling
IMPROVED: DB: more tolerant rollback() [thanks lothar]
IMPROVED: DB: fingerprinter
IMPROVED: DICOM: dicomization
IMPROVED: DB: settings logging
IMPROVED: login: DB sanity checking
IMPROVED: cfg: logging of set-option errors, forward-ported
IMPROVED: allergy handling
IMPROVED: hints: gracefully handle failing dynamic hints
IMPROVED: document archive: add image/text preview
IMPROVED: PACS: host default
IMPROVED: PACS: show new patients following a DICOM import
IMPROVED: safe patient data into gnumed/patients/ instead of gnumed/
IMPROVED: forms: vaccination history LaTeX template
IMPROVED: lists: make minimum column width policy configurable [thanks María]
IMPROVED: buttons: make shrinking to label size configurable [thanks María]
IMPROVED: datetime picker: support "Today/toMorrow/Yesterday = day X" syntax

FIX: CLI: --wxp= not needed anymore
FIX: CLI: --ui= not needed anymore
FIX: documentation: links (wiki -> static pages)
FIX: date/time: formatting intervals medically
FIX: Py3.13: will remove mailcap module
FIX: forward-port fix for grid selection constant names
FIX: Py3.13: removed packaging.version from stdlib [thanks María]

DEP: removed LibreOffice forms engine

	23.0

NEW: add list position to export items
NEW: add intake regimen support
NEW: bootstrapper: auto-fix collations as needed
NEW: bootstrapper: adjust view settings to security_definer (requires PG15)
NEW: support for gender symbols stored in DB
NEW: bootstrapper: support for connection environment variables

IMPROVED: bootstrap script permissions warning
IMRPOVED: clin.v_narrative4search: add some demographics (port from 1.8.6)
IMPROVED: bootstrapper: code cleanup

FIX: PG14 does not support IS OF anymore, use pg_typeof()
FIX: revoke CREATE from PUBLIC on schema PUBLIC (thanks PG)
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-release_notes-dynamic.sql', '23.0');
