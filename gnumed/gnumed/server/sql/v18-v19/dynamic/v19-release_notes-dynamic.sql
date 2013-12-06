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
	'Release Notes for GNUmed 1.4.4 (database v19.4)',
	'GNUmed 1.4.4 Release Notes:

	1.4.4

FIX: gracefully recover from invalid URLs [thanks Jim]
FIX: encounter editing from EMR browser [thanks Jim]
FIX: faulty date access in test result EA [thanks Jim]
FIX: a few minor bugs displaying test results

IMPROVED: results formatting in episode synopsis of EMR tree
IMPROVED: lots of details in the test results grid

	19.4 -- Requires PostgreSQL 9.1 !
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.rc2');
