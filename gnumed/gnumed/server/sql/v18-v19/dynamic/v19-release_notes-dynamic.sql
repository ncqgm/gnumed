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
	'Release Notes for GNUmed 1.4.13 (database v19.13)',
	'GNUmed 1.4.13 Release Notes:

	1.4.13

FIX: attempt to remove all items from a bill [thanks Marc]
FIX: exception on adding improperly selected bill item [thanks Marc]
FIX: exception on trying to add duplicate keyword expansion [thanks Marc]

	19.13 -- Requires PostgreSQL 9.1 !
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.8');
