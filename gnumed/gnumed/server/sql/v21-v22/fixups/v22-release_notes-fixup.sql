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
	'Release Notes for GNUmed 1.8.9 (database v22.19)',
	'GNUmed 1.8.9 Release Notes:

	1.8.9

FIX: mime handling: py3 adjustments in file magic [thanks Andreas]
FIX: bills: exception on generating invoice PDF [thanks l-ray]
FIX: about: exception in about dialog [thanks aimee]

	22.19

FIX: bootstrapper: no more IS OF, use pg_typeof in v2->v3 transition [thanks Lennart]
FIX: bootstrapper: CHAR -> TEXT cast in v19+ schema hashing on recent PGs
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.19@1.8.9');
