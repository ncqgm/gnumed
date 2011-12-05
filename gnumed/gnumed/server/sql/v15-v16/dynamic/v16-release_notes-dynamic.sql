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
	'Release Notes for GNUmed 1.1.7 (database v16.7)',
	'GNUmed 1.1.7 Release Notes:

	1.1.7

IMPROVED: warn on saving branded drugs w/o components [thanks vbanait]

FIX: do not check .is_vaccine against None [thanks J.Busser]
FIX: failure to access drug database on reconfiguration of invalid preselect [thanks J.Busser]
FIX: inability to edit a drug component intake [thanks S.Hilbert]
');

-- --------------------------------------------------------------
