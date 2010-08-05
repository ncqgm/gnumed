-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
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
	'Release Notes for GNUmed 0.8.0 (database v14.0)',
	'GNUmed 0.8.rc2 Release Notes:

NEW: Add button to lookup drug on www.dosing.de to current substances plugin.
NEW: hook: "after_soap_modified"
NEW: placeholder: "current_meds_table::latex"
NEW: placeholder: "current_meds_notes::latex"
NEW: placeholder: "lab_table::latex"
NEW: placeholder: "latest_vaccs_table::latex"
NEW: score: Rome diagnostic criteria on obstipation
NEW: score: Cincinatti Stroke Scale (F.A.S.T.)
NEW: score: bacterial UTI algorithm
NEW: score: coronary artery disease in primary care
NEW: score: ABCDEF & Glasgow-7-points for identifying atypical moles
NEW: report: patients taking drug X
NEW: graphing of ranges of measurements (user-defined gnuplot scripts)
NEW: support emergency contact
NEW: support comment directly on identity
NEW: Add button to report ADR from within current substances plugin.
NEW: list view of database audit trail
NEW: management of vaccinations and vaccines
NEW: templates for writing a plugin [thanks S.Hilbert]
NEW: on Windows try to switch to "DejaVu Sans" font for improved unicode display
NEW: demonstrable path to get up and running on Macintosh [thanks J.Busser]
NEW: useful error dialog when database connection lost
NEW: email log file on demand from menu
NEW: support Canadian MSVA format as external patient source

IMPROVED: GNUmed can now import the ARRIBA result as a document
IMPROVED: rename client/locale/ to client/po/ and adjust to that
IMPROVED: when enabling --debug during unhandled exception try harder to log the exception in question
IMPROVED: more robust acquiring of data from image sources
IMPROVED: more medically-sound interval formatting
IMPROVED: another, more expected, way of calculating patient age
IMPROVED: edit non-name identity parts *directly* in demographics plugin (no popup needed)
IMPROVED: show date-generated in patient picture tooltip
IMPROVED: much better icon [thanks J.Jaarsveld]
IMPROVED: show comment/emergency contact in patient search control tooltip
IMPROVED: re-add encounters to auditing
IMPROVED: show loinc info for test in test results EA
IMPROVED: much smarter result units phrasewheel
IMPROVED: DOB validity check when creating new person
IMPROVED: better layout of configuration listing
IMPROVED: medication formatting
IMPROVED: current medication patient handout [thanks C.Hilbert]
IMPROVED: pre-filter form template selection list based on purpose of showing
IMPROVED: default config file for running from tarball
IMPROVED: better support FreeDiams (0.4.2 now in Debian)
IMPROVED: EMR tree root note context menu
IMPROVED: generic lists can now have 3 extra buttons
IMPROVED: use substance rather than brand as allergene when creating allergy from substance intake entry
');

-- --------------------------------------------------------------
