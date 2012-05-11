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
	'Release Notes for GNUmed 1.1.14 (database v16.14)',
	'GNUmed 1.1.14 Release Notes:

	1.1.14

FIX: missing pre-save date verification in document properties editor [thanks J.Busser]
FIX: exception on procedure start > end [thanks J.Busser]
FIX: corner case of faulty drug database selection [thanks J.Busser]
');

-- --------------------------------------------------------------
