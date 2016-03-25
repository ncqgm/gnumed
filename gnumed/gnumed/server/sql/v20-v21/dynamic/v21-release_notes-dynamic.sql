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
	'Release Notes for GNUmed 1.6.2 (database v21.2)',
	'GNUmed 1.6.2 Release Notes:

	1.6.2

FIX: exception create consumable substance by ATC
FIX: exception on showing files of new document
FIX: exception on saving new document
FIX: exception on saving substance abuse entry
FIX: exception on attempting to apply sorting outside list column

	1.6.1

FIX: gm-describe_file missing in tarball

IMPROVED: manpages for gm-create_dicomdir/gm-create_datamatrix

	21.2

NEW: implement commenting out of plausibility checks

IMPROVED: run all plausibility checks even if any fail
IMPROVED: more resilience against malformed plausibility checks

FIX: inaccurate dem.v_staff plausibility check [thanks Marc]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.2');
