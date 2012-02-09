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
	'Release Notes for GNUmed 1.1.12 (database v16.12)',
	'GNUmed 1.1.12 Release Notes:

	1.1.12

FIX: exception with certain invalid placeholders [thanks S.Reus]
FIX: add missing encoding detection [thanks Andrew]
FIX: broken health issue creation from its PRW [thanks S.Reus]

IMPROVED: robustify os.startfile() use [thanks S.Hilbert]
IMPROVED: robustify auto-setting of encounter.last_affirmed
IMPROVED: robustify validity checks of cFuzzyTimestampInput [thanks S.Reus]
IMPROVED: overly eager page number collision check [thanks S.Hilbert]
');

-- --------------------------------------------------------------
