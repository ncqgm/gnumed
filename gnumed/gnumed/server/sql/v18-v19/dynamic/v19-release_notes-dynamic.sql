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
	'Release Notes for GNUmed 1.4.11 (database v19.11)',
	'GNUmed 1.4.11 Release Notes:

	1.4.11

FIX: failing Creatinine vs GFR age calculation
FIX: failure to handle pre-1900''s measurements

IMPROVED: date format in bill/bill_item placeholder [thanks Marc]
IMPROVED: auto-selection of bill receiver address [thanks Marc]

	19.11 -- Requires PostgreSQL 9.1 !

IMPROVED: sorting of bill item PKs in bills view [thanks Marc]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.8');
