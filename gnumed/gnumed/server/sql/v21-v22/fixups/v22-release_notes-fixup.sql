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
	'Release Notes for GNUmed 1.8.7 (database v22.18)',
	'GNUmed 1.8.7 Release Notes:

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
NEW: dist: add PortableApp XML skeleton
NEW: placeholder: $most_recent_test_results$
NEW: tool: check_mimetypes_in_archive

	22.18

IMPROVED: bootstrapper: schema "public" permissions and ownership as per PG 15
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.18@1.8.7');
