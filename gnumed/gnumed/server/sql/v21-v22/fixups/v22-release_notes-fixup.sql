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
	'Release Notes for GNUmed 1.8.2 (database v22.12)',
	'GNUmed 1.8.2 Release Notes:

	1.8.2

FIX: dicom: exception on uploading malformed DCM to Orthanc
FIX: dicom: exception on failing to download a DCM from Orthanc
FIX: MacOSX: exception on wx.EndBusyCursor w/o wx.BeginBusyCursor [thanks Alex]
FIX: database: fix connection pooling [thanks various]

IMPROVED: lab: by-day display functionality
IMPROVED: emr: tree: more informative display
IMPROVED: main menu: put <export area> under <paperwork>
IMPROVED: PACS: display RequestingOrg
IMPROVED: bootstrap: password input [thanks bganglia892]
IMPROVED: wxPython: robustify on force-ASSERT devel builds [thanks bganglia892]
IMPROVED: startup: logging of execution environment
IMPROVED: shutdown: one more code path for exception handling abort
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.13');
