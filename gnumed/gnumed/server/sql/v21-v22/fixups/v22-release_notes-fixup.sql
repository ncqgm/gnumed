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
	'Release Notes for GNUmed 1.7.9 (database v22.9)',
	'GNUmed 1.7.9 Release Notes:

	1.7.9

FIX: billing: invoice ID generation [thanks Marc]
FIX: dist: GNUmed Manual d/l URL
FIX: template: letter w/ & w/o Dx-s
FIX: paperwork: letter receiver dlg address selection
FIX: EMR/tree: exception on loading visual progress notes

	22.9

FIX: clin.v_candidate_diagnoses: missing coalesce()
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.9');
