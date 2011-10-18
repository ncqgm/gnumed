-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
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
	'Release Notes for GNUmed 0.9.11 (database v15.11)',
	'GNUmed 0.9.11 Release Notes:

	0.9.11

IMPROVED: add SQL reports to find duplicate streets/urbs/regions

	15.11

FIX: trf_do_not_substance_if_taken_by_patient() on ref.consumable_substance
FIX: missing E in front of escape-syntax strings in SQL bootstrap files
');

-- --------------------------------------------------------------
