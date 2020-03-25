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
	'Release Notes for GNUmed 1.8.1 (database v22.12)',
	'GNUmed 1.8.1 Release Notes:

	1.8.1

NEW: tool: read_all_rows_of_table

FIX: bills: failure to generate bill PDFs [thanks Marc]
FIX: bills: failure to edit bill item date [thanks Marc]
FIX: bills: failure to edit billable [thanks Marc]
FIX: export area: fails to load when gm-burn.sh not found [thanks Marc]
FIX: demographics: failure to edit type of address [thanks Marc]
FIX: forms: failure to archive generated forms [thanks Marc]
FIX: demographics: faulty display of patient addresses [thanks Marc]

	22.12

IMPROVED: robustify backup script
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.12');
