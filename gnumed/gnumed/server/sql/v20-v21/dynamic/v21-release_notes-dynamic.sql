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
	'Release Notes for GNUmed 1.6.3 (database v21.3)',
	'GNUmed 1.6.3 Release Notes:

	1.6.3

FIX: exception on creating invoice from bill [thanks Marc]
FIX: faulty assumption on what %()s keys must exist in translations
FIX: exception in expando SOAP editor when lines need wrapping [thanks Marc]
FIX: exception on saving progress note under new episode [thanks Marc]
FIX: exception on deleting list items [thanks Marc]
FIX: exception on building list context menu [thanks Marc]
FIX: exception in measurements widget on client idling w/o patient [thanks Marc]

IMPROVED: add httplib2 to check-prerequisites.py [thanks Marc]
IMPROVED: single-line formatting of addresses
IMPROVED: enhance list context menu to selected rows

	21.3

FIX: GRANTs on demographics views [thanks Marc]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.3');
