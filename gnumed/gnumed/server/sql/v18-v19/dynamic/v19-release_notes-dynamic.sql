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
	'Release Notes for GNUmed 1.4.10 (database v19.10)',
	'GNUmed 1.4.10 Release Notes:

	1.4.10

IMPROVED: labelling of sign vs review in measurements EA [thanks Jim]
IMPROVED: coloring of abnormals [thanks Jim]
IMPROVED: wxpython 3 compatibility

	19.10 -- Requires PostgreSQL 9.1 !

FIX: overly eager INNER JOIN of dem.v_praxis_branch
FIX: overly eager INNER JOINs of dem.v_orgs/dem.v_org_units [thanks Jim]
FIX: do not reuse tx after failure of "ignore_checksum_failure" on PG < 9.3

IMPROVED: more robust pg_trgm installation
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.8');
