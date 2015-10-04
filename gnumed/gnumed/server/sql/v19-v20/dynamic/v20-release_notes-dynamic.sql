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
	'Release Notes for GNUmed 1.5.7 (database v20.7)',
	'GNUmed 1.5.7 Release Notes:

	1.5.7

FIX: one more nonissue-problem tooltip exception in SOAP editor [thanks Marc]
FIX: encounter change exception on patient change w/ multiple clients [thanks Marc]
FIX: patient overview tooltip exception on patient change [thanks Marc]
FIX: mysterious non-problem with missing "Gnumed." in import [thanks Basti]
FIX: symlink creation on Windows

IMPROVED: logging of payload changes in case of conflict
IMPROVED: early startup logging
IMPROVED: show low file location during startup
IMPROVED: windows startup batch file
IMPROVED: redirect wxPython log to python logging
IMPROVED: set wxPython AssertMode appropriately

	20.7

no changes
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-release_notes-dynamic.sql', '20.7');
