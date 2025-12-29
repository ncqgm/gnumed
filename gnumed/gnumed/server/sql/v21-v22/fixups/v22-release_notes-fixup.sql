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
	'Release Notes for GNUmed 1.8.23 (database v22.33)',
	'GNUmed 1.8.23 Release Notes:

	1.8.23

FIX: hyphenated module names failing in newer Python versions [thanks María]

IMPROVED: UI: cfg: notebook tabs position [thanks María]
IMPROVED: DB: warn on non-SCRAM passwords

	22.33

FIX: boostrapping: gm-dbo cannot GRANT ...  WITH ADMIN to itself
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.33@1.8.23');
