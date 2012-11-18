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
	'Release Notes for GNUmed 1.2.6 (database v17.6)',
	'GNUmed 1.2.6 Release Notes:

	1.2.6

FIX: failure to merge patients with identical names [thanks S.Reus]
IMPROVED: Backport looking at config files when scanning for installed plugins

	17.6

FIX: very senior installations might have duplicate blobs.doc_obj.fk_doc FK defs
IMPROVED: extend range of guard against all-zero substance amount fractions
');

-- --------------------------------------------------------------
