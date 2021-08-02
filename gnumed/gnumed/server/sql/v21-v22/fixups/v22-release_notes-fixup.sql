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
	'Release Notes for GNUmed 1.8.6 (database v22.16)',
	'GNUmed 1.8.6 Release Notes:

	1.8.6

FIX: unlocking encounters (missing import)
FIX: row locking code
FIX: metadata: screenshots URL in appdata.xml
FIX: GUI: screenshot function [thanks The-o]
FIX: medical interval formatting [thanks brulefa]
FIX: date/time input: time parsing
FIX: date/time input: function key to weekday mapping
FIX: encounters: do not crash if current encounter is deleted
FIX: paperwork: fix emr_journal placeholder LaTeX escaping [thanks Marc]

IMPROVED: desktop entry file [thanks freddii]
IMPROVED: patient switch: encounter checking
IMPROVED: pat overview: problems display
IMPROVED: DB: connection loss detection
IMPROVED: measurement EA: previous result formatting
IMPROVED: DB: login problem logging
IMPROVED: top pane: show age of results in tooltip
IMPROVED: paperwork: LaTeX formatting of text
IMPROVED: EMR: extend search to select demographics [thanks brulefa]
IMPROVED: startup: bash code [thanks shellcheck]

	22.16

IMPROVED: bootstrapper: check disk space

FIX: check encounter lock in clin.remove_old_empty_encounters()
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.16@1.8.6');
