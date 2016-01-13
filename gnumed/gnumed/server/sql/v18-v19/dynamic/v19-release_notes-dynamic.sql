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
	'Release Notes for GNUmed 1.4.16 (database v19.16)',
	'GNUmed 1.4.16 Release Notes:

	1.4.16

FIX: exception in staff list if there is staff with deleted DB account

	19.16 -- Requires PostgreSQL 9.1 !

FIX: pg_trgm placement and use
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.16');
