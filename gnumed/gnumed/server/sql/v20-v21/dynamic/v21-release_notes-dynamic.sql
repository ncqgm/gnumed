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
	'Release Notes for GNUmed 1.6.7 (database v21.7)',
	'GNUmed 1.6.7 Release Notes:

	1.6.7

FIX: constrain hospital stay PRW to current patient
FIX: smoking status detection in dynamic hints
FIX: GKV checkup auto hint
FIX: tetanus shot auto hint
FIX: substance intake discontinuation reason field behaviour
FIX: exception in clinical calculator with pre-birth test results

IMPROVED: file viewer detection on Windows [thanks John]
IMPROVED: DICOM studies/series display
IMPROVED: ZIP-with-DICOMDIR support
IMPROVED: browse index.html after saving/burning from export area
IMPROVED: substance abuse management workflow
IMPROVED: check for tools im gm-describe_file
IMPROVED: substance intake start/end formatting

NEW: a few hints from the German Choosing Wisely initiative
NEW: CD/DVD sleeve LaTeX template
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.6');
