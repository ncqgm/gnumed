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
	'Release Notes for GNUmed 0.9.2 (database v15.2)',
	'GNUmed 0.9.2 Release Notes:

Client 0.9.2

	IMPROVED: German translation [thanks S.Hilbert]
	IMPROVED: units PRW now also pulls from ATC DDD and consumable substances amount [thanks S.Hilbert]

Database 15.2

	FIX: unjudicious use of "set -e" creates more problems than it solves
');

-- --------------------------------------------------------------
