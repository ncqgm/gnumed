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
	'Release Notes for GNUmed 1.6.15 (database v21.15)',
	'GNUmed 1.6.15 Release Notes:

	1.6.15

FIX: exception on tooltipping patient overview inbox item
FIX: exception in cursor/connection state logging w/ older psycopg2s
FIX: exception on import error inside portable app

IMPROVED: use Dicom[RequestingPhysician] if available
IMPROVED: user visible rendering of raw DICOM strings
IMPROVED: baptize SCRAM for PG passwords in settings check

	21.15

FIX: handle SQL_INHERITANCE in a way compatible with PG10
FIX: untyped UNIONs not tolerated by PG10 anymore
FIX: RETURNS UNKNOWN functions not tolerated by PG10 anymore

IMPROVED: script to adjust db settings
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.15');
