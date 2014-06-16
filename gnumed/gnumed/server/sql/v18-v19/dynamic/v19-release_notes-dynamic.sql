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
	'Release Notes for GNUmed 1.4.9 (database v19.9)',
	'GNUmed 1.4.9 Release Notes:

	1.4.9

FIX: bug in current_meds placeholder
FIX: utterly slow praxis branch PRW [thanks Jim]
FIX: bug with changing praxis definition

	19.9 -- Requires PostgreSQL 9.1 !

IMPROVED: add some indices to dem.org(_unit)
IMPROVED: faster view for praxis branches
IMPROVED: add pg_trgm extension
IMPROVED: speed of dem.v_org_units

');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.8');
