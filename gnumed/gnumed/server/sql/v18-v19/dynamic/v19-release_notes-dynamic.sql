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
	'Release Notes for GNUmed 1.4.2 (database v19.2)',
	'GNUmed 1.4.2 Release Notes:

	1.4.2

FIX: mislinked document insert [thanks Marc]

IMPROVED: desktop entry keywords [thanks Andreas]
IMPROVED: man page typo [thanks Andreas]
IMPROVED: authentication environment logging
IMPROVED: patient overview encounters summary [thanks Jim]

	19.2 -- Requires PostgreSQL 9.1 !

IMPROVED: normalization of (clin.procedure/clin.hospital_stay).fk_org_unit
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.rc2');
