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
	'Release Notes for GNUmed 1.7.8 (database v22.8)',
	'GNUmed 1.7.8 Release Notes:

	1.7.8

FIX: billing: invoice ID template configuration [thanks Marc]
FIX: config: top pane lab panel setting [thanks Jelle Mous]
FIX: searching across active EMR [thanks Eberhard]

	22.8

FIX: i18n.set_curr/force_curr_lang()
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.8');
