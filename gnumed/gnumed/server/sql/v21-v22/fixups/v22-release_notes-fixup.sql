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
	'Release Notes for GNUmed 1.7.6 (database v22.6)',
	'GNUmed 1.7.6 Release Notes:

	1.7.6

FIX: application metadata files
FIX: searching across all EMRs
FIX: constrain document PRW to current patient
FIX: lab/table: exception on double-clicking empty cell in row w/o meta test type
FIX: lab/result EA: failure to show test type on edit

NEW: stub out $praxis_scan2pay$

	22.6

FIX: properly include fixups in v21-v22 upgrade

IMPROVED: database backup script
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.6');
