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
	'Release Notes for GNUmed 1.5.6 (database v20.6)',
	'GNUmed 1.5.6 Release Notes:

	1.5.6

FIX: exception on removing temporary config file [thanks Vaibhav]
FIX: exception on importing duplicate file into export area
FIX: exception on merging patients under wxPython 3 [thanks max]

	20.6

no changes
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-release_notes-dynamic.sql', '20.6');
