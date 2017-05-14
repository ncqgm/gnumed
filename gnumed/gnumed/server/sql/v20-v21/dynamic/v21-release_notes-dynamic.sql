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
	'Release Notes for GNUmed 1.6.13 (database v21.13)',
	'GNUmed 1.6.13 Release Notes:

	1.6.13

FIX: editing of drug products
FIX: formatting of intervals with seconds [thanks Rickard]
FIX: robustify backend listener against change notification trigger errors
FIX: backport once-only detection of unicode char selector
FIX: improper handling of notebook page change events
FIX: error handling on uploading DICOM to Orthanc

IMPROVED: more fully prevent logfile based password leaks
IMPROVED: add listing of latest vaccination per indication
IMPROVED: export area change listening and sortability
IMPROVED: episode edit area behaviour
IMPROVED: add measurement by clicking empty cell in grid

NEW: add Constans algorithm for upper extremity DVT
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.13');
