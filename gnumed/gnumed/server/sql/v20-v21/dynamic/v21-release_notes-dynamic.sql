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
	'Release Notes for GNUmed 1.6.5 (database v21.5)',
	'GNUmed 1.6.5 Release Notes:

	1.6.5

IMPROVED: list context menu: operate on _selected_ rows

	1.6.4

FIX: EMR journal exporter on Windows [thanks Marc]

IMPROVED: by-org sort mode in document tree
IMPROVED: file describer script
IMPROVED: STIKO tetanus auto hint
IMPROVED: ES translation [thanks Uwe]

NEW: gm-import_incoming script for external use
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.5');
