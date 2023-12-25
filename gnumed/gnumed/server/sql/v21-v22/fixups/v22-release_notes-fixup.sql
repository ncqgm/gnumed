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
	'Release Notes for GNUmed 1.8.17 (database v22.27)',
	'GNUmed 1.8.17 Release Notes:

	1.8.17

FIX: patient search exception
FIX: OOo startup exception
FIX: placeholders today/date_of_birth/name parsing if no format given
FIX: logging of invalid form templates
FIX: logging of invalid address data

IMPROVED: EMR browser: link document review dlg from document nodes
IMPROVED: configuration: logging of set-option failures

	22.27

NEW: add systemd .timer/.service files for scheduling database backup
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.27@1.8.17');
