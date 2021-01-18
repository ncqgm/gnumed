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
	'Release Notes for GNUmed 1.8.5 (database v22.15)',
	'GNUmed 1.8.5 Release Notes:

	1.8.5

FIX: image conversion w/o target extension [thanks ...]
FIX: SVG icon [thanks freddii]
FIX: lab: tab "most-recent": [x]ing "show missing" throws exception
FIX: log: exception on inaccessible attributes

NEW: add CoVid-2019 vaccines

	22.15

FIX: message inbox view
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.15@1.8.5');
