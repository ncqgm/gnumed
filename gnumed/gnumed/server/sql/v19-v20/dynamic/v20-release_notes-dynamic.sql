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
	'Release Notes for GNUmed 1.5.1 (database v20.1)',
	'GNUmed 1.5.1 Release Notes:

	1.5.1

FIX: include pregnancy widgets with tarball
FIX: do not require JSON in psycopg2 [thanks Jim]

	20.1

IMPROVED: database restore script [thanks Jim]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-release_notes-dynamic.sql', '20.0');
