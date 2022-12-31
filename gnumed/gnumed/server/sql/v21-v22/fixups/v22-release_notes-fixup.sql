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
	'Release Notes for GNUmed 1.8.8 (database v22.18)',
	'GNUmed 1.8.8 Release Notes:

	1.8.8

IMPROVED: PACS: better image/image buttons placement

FIX: py3.10+ *requires* ints for rescaling images [thanks henrique]
FIX: patient tags: do not crash when rescaling image fails [thanks henrique]
FIX: fix a number of errors found by pyflakes3
FIX: lists: no more wx.LIST_HITTEST_ONITEMRIGHT in wxPython 4.2 [thanks jonas]
FIX: date/time input: exception on entering "0"

	22.18

IMPROVED: bootstrapper: schema "public" permissions and ownership as per PG 15
IMPROVED: backup: avoid unnecessary recompression

FIX: bootstrapper: schema hash function in v19+ databases
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.18@1.8.8');
