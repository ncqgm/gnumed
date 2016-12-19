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
	'Release Notes for GNUmed 1.6.11 (database v21.11)',
	'GNUmed 1.6.11 Release Notes:

	1.6.11

IMPROVED: edit area refresh on first setting data
IMPROVED: DB link error logging
IMPROVED: suppressed hints display in patient overview
IMPROVED: sorting of Hx items in patient overview
IMPROVED: use of pdfinfo in gm-describe_file

FIX: stall of gm-create_datamatrix in swap storm
FIX: BMP creation without substance intakes
FIX: missing quotes in BMP datafile [thanks Moritz]
FIX: failure to sometimes store progress notes [thanks Marc]
FIX: exception on double-clicking document tree label node
FIX: exception on switching to drug database frontend [thanks a sk_SK]
FIX: exception on saving hospital stay [thanks a sk_SK]
FIX: exception on checking for upgrade [thanks Philipp]

	21.11

IMPROVED: backup scripts error checking

FIX: serialization failures due to table mod announcement triggers
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.11');
