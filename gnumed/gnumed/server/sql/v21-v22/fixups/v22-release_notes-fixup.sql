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
	'Release Notes for GNUmed 1.7.1 (database v22.1)',
	'GNUmed 1.7.1 Release Notes:

	1.7.1

NEW: add bash completion script

IMPROVED: make DWV optional
IMPROVED: prerequisites check tool
IMPROVED: update timeline code to 1.17.0 release

	22.1

IMPROVED: concurrency robustness of backup/restore scripts
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.1');
