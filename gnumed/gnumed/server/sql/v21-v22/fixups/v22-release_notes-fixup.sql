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
	'Release Notes for GNUmed 1.8.10 (database v22.20)',
	'GNUmed 1.8.10 Release Notes:

	1.8.10

FIX: bills: exception on saving invoice PDF [thanks Aimee]
FIX: orgs: deleting org unit used by external care [thanks Aimee]
FIX: forms: managing addresses from letter receiver selection [thanks Aimee]
FIX: episode PRW: only search matches if patient is set [thanks Marc]

	22.20

No changes over 22.19.
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.20@1.8.10');
