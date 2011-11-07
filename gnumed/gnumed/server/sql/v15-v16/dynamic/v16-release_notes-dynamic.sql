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
	'Release Notes for GNUmed 1.1.2 (database v16.2)',
	'GNUmed 1.1.2 Release Notes:

	1.1.2

FIX: faulty access to _TCTRL_unit in patient creation widgets [thanks J.Busser]

IMPROVED: confirm removing patients from the waiting list [thanks J.Busser]
IMPROVED: remove misleading "There are no encounters for this episode." [thanks J.Busser]

	16.2

FIX: properly export GM_LOG_BASE in scripts [thanks Debian]
');

-- --------------------------------------------------------------
