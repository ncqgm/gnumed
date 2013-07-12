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
	'Release Notes for GNUmed 1.3.7 (database v18.7)',
	'GNUmed 1.3.7 Release Notes:

	1.3.7

FIX: exception on substance intake w/o start date [thanks Jim]
FIX: faulty SQL in lab phrasewheel [thanks Jim]
FIX: exception on saving modified organization [thanks Jim]
FIX: validity check on substance discontinuation date [thanks Jim]
FIX: exception on accessing org unit comm channel comment [thanks Jim]
FIX: failure to properly delete org *units* [thanks Jim]
FIX: failure to properly edit substance intakes [thanks Jim]

IMPROVED: show substance intolerances in magenta rather than yellow [thanks Jim]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.5');
