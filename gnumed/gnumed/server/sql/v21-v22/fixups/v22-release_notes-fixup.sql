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
	'Release Notes for GNUmed 1.8.16 (database v22.26)',
	'GNUmed 1.8.16 Release Notes:

	1.8.16

FIX: SQL plugin: exception on faulty query
FIX: meds plugin: grid selection constant names
FIX: gtk: do not abort on sizer flags inconsistencies in production code

IMPROVED: plugin PACS: layout
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.26@1.8.16');
