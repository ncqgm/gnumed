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
	'Release Notes for GNUmed 1.7.3 (database v22.3)',
	'GNUmed 1.7.3 Release Notes:

	1.7.3

FIX: failure to merge patients under some conditions [thanks Marc]
FIX: exception on creating person duplicates
FIX: failure to delete inbox messages w/o a receiver
FIX: handling of single_selection in generic list selection [thanks Scott Talbert]
FIX: setting of initial size of main frame [thanks Tim Roberts]

IMPROVED: robustify tarballing script against network flukes
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.3');
