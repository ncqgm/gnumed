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
	'Release Notes for GNUmed 1.8.4 (database v22.14)',
	'GNUmed 1.8.4 Release Notes:

	1.8.4

IMPROVED: exceptions: always include exception/traceback in mail
IMPROVED: PACS: robustify DICOM upload

FIX: placeholders: exception on parsing some option styles
FIX: address: nominatim.openstreetmap.org API has changed
FIX: documents: properly wipe details display between patients

	22.14

FIX: bootstrapper exception calling capture_conn_state()
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.14@1.8.4');
