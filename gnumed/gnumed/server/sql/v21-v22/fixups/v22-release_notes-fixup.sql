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
	'Release Notes for GNUmed 1.8.15 (database v22.25)',
	'GNUmed 1.8.15 Release Notes:

	1.8.15

IMPROVED: person search: query speed

	1.8.14

FIX: plugins: exception on raising configured but unloaded plugin

IMPROVED: SOAP: on patient change ask if unsaved SOAP [thanks Marc]
IMPROVED: DB: setup connections for auto_explain in --debug mode

	22.25

IMPROVED: identity/names: indices

	22.24

IMPROVED: blobs: indices [thanks Marc]

FIX: waiting list: failure in function moving entries
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.25@1.8.15');
