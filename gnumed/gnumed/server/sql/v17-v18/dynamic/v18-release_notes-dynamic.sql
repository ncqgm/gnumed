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
	'Release Notes for GNUmed 1.3.5 (database v18.5)',
	'GNUmed 1.3.5 Release Notes:

	1.3.5

FIX: exception on merging patients with identical external IDs [thanks Jim]

IMPROVED: further clarify license of Timeline icons

	18.5

no changes
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.5');
