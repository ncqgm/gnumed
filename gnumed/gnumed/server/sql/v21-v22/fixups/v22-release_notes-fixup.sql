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
	'Release Notes for GNUmed 1.8.25 (database v22.35)',
	'GNUmed 1.8.25 Release Notes:

	1.8.25

IMPROVED: speed of document part access [thanks Marc]

	22.35

IMPROVED: speed of i18n._() [thanks Marc]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.35@1.8.25');
