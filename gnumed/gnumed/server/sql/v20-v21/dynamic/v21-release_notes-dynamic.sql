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
	'Release Notes for GNUmed 1.6.14 (database v21.14)',
	'GNUmed 1.6.14 Release Notes:

	1.6.14

FIX: exception when having issues with calculating eGFR in medication plugin
FIX: exception on disabling identity [thanks Marc]
FIX: exception on adding archived documents to export area
FIX: Orthanc DICOM patient ID modification
FIX: faulty file drop target declarations

IMPROVED: saving of export area items
IMPROVED: patient display in provider inbox
IMPROVED: copy document to export area from document plugin
IMPROVED: Orthanc modification dialog title
IMPROVED: imported documents deletion confirmation
IMPROVED: patient media metadata
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.14');
