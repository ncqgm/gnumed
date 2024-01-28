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
	'Release Notes for GNUmed 1.8.18 (database v22.28)',
	'GNUmed 1.8.18 Release Notes:

	1.8.18

IMPROVED: new-patient: dialog layout
IMPROVED: phrasewheels: in-focus signalling
IMPROVED: less diagnostic GTK output on console

	22.28

FIX: concatenation of the database schema structure

IMPROVED: documentation for backup systemd .service file
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.28@1.8.18');
