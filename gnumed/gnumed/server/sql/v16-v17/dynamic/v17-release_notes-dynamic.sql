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
	'Release Notes for GNUmed 1.2.3 (database v17.3)',
	'GNUmed 1.2.3 Release Notes:

	1.2.3

FIX: failure to parse plugin directory with frozen app [thanks S.Hilbert]
FIX: failure to add >1 branded intake in sequence [thanks V.Banait]
FIX: exception on saving hospital stay w/o admission date
FIX: failure to check for message expiry > due [thanks S.Griesfeller]
');

-- --------------------------------------------------------------
