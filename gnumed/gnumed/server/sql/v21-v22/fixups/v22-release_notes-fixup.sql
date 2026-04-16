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
	'Release Notes for GNUmed 1.8.24 (database v22.34)',
	'GNUmed 1.8.24 Release Notes:

	1.8.24

FIX: more robust UI update when quickly scrolling document tree
FIX: more robust handling of DICOM instance download issues
FIX: more robust Orthanc DICOM instance parsing

	22.34

FIX: bootstrapping: chicken-egg-problem with gm-dbo vs groups creation
FIX: bootstrapping: use pg_roles rather than pg_user b/c of collation dependance
FIX: gm.transfer_users(): switch from pg_user to pg_roles
FIX: bootstrapping: properly set ADMIN on groups when running several upgrades in a row
FIX: bootstrapping: using CREATE ROLE for users requires explicit LOGIN
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.34@1.8.24');
