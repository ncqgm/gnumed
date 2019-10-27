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
	'Release Notes for GNUmed 1.8.0rc1 (database v22.8)',
	'GNUmed 1.8.0rc1 Release Notes:

	1.8.0

NEW: port to wxPython 4 (wxPhoenix)
NEW: port to Python 3
NEW: port bootstrapper to Python 3

NEW: EMR tree: toggle episode status from context menu
NEW: EMR tree: show/edit clinical items from below encounters
NEW: ReST formatting in $free_text::::$ placeholder
NEW: hook "after_waiting_list_modified"
NEW: test results tab showing most-recent in test panel
NEW: local documents cache
NEW: systemd-tmpfiles config file
NEW: emailing of export area content as encrypted zip file
NEW: local directory entries in export area
NEW: $praxis_scan2pay$ support
NEW: $bill_scan2pay$ support
NEW: status bar history/visual bell
NEW: dicomize images/PDF into DICOM study
NEW: [Abort] client from exception dialog
NEW: edit clinical item from EMR list journal

IMPROVED: symbolic link creation on Windows
IMPROVED: Orthanc connection handling
IMPROVED: DICOM plugin UI
IMPROVED: EMR export as TimeLine
IMPROVED: captions of all list and edit area dialogs
IMPROVED: test type edit area workflow
IMPROVED: CLI EMR export tool
IMPROVED: form disposal dialog
IMPROVED: date/timestamp picker functionality
IMPROVED: better duplicate person detection
IMPROVED: document tree details view usage
IMPROVED: test results panels links w/ documents
IMPROVED: console encoding errors behaviour [thanks INADA Naoki]
IMPROVED: ADR URL handling
IMPROVED: age sort mode in document tree
IMPROVED: age/DOB tooltip
IMPROVED: data revisions display
IMPROVED: EMR list journal formatting
IMPROVED: lab/plotting: support better gnuplot scripts

FIX: [Save] functionality of Export Area
FIX: document tree sorting / document insertion
FIX: inability to delete inbox message w/o receiver
FIX: "lastname, firstname" based patient search under Python 3


	22.8

FIX: i18n.set_curr/force_curr_lang()

	22.7

IMPROVED: lab results plotting scripts for gnuplot
IMPROVED: bills tables grants for invoice ID generation

NEW: multi-results plotting script for gnuplot

	22.6

FIX: properly include fixups in v21-v22 upgrade

IMPROVED: database backup script
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.8');
