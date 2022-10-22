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
	'Release Notes for GNUmed 1.8.7 (database v22.18)',
	'GNUmed 1.8.7 Release Notes:

	1.8.7

FIX: export area: dumping encrypted/PDFed image to disk
FIX: top panel: heart rate display
FIX: paperwork: recalls list LaTeX template

	22.18

IMPROVED: bootstrapper: schema "public" permissions and ownership as per PG 15
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.18@1.8.7');
