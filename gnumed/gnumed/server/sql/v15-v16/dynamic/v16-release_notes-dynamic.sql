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
	'Release Notes for GNUmed 1.1.10 (database v16.10)',
	'GNUmed 1.1.10 Release Notes:

	1.1.10

IMPROVED: arriba now at version 2.4.1
IMPROVED: support non-blocking external apps on Windows [thanks S.Hilbert]
IMPROVED: offline docs [thanks S.Hilbert]
IMPROVED: russian translation [thanks YvLy]

FIX: bug in calculating apparent age when patient is born later today
');

-- --------------------------------------------------------------
