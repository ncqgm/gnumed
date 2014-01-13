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
	'Release Notes for GNUmed 1.4.5 (database v19.5)',
	'GNUmed 1.4.5 Release Notes:

	1.4.5

	FIX: permissions of ${TMP}/gnumed/ on multiuser systems [thanks Kalle]

	IMPROVED: lab results grid tooltips
	IMRPOVED: manage test types from lab results grid
	IMRPOVED: manage aggregates from test types listing
	IMPROVED: temporary directory

	19.5 -- Requires PostgreSQL 9.1 !

	FIX: gm-adjust_db_settings.sh to work from non-CWD [thanks Marc]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.rc2');
