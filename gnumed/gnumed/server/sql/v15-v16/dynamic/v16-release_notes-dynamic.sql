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
	'Release Notes for GNUmed 1.1.6 (database v16.6)',
	'GNUmed 1.1.6 Release Notes:

	1.1.6

FIX: missing check for substance intake end date in the future [thanks S.Hilbert]
FIX: faulty search query for persons w/o a title [thanks J.Busser]
FIX: failure to verify substance intake duration [thanks vbanait]

IMPROVED: description w/ gender formatting [thanks J.Busser/Liz]
IMPROVED: EMR tree browser: remove redundant gender from root item tooltip
IMPROVED: demographics: protect against deletion of active name [thanks J.Busser]
IMPROVED: gracefully fail attempts to duplicate drug component intake [thanks S.Hilbert]

	16.6

FIX: remove faulty i18n-fixup ("generic" tx target does not work as expected) [thanks J.Busser]

IMPROVED: robustify log directory setting in bootstrapper scripts [thanks S.Hilbert]
');

-- --------------------------------------------------------------
