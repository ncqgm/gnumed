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
	'Release Notes for GNUmed 1.3.6 (database v18.6)',
	'GNUmed 1.3.6 Release Notes:

	1.3.6

FIX: exception on merging patients with identical addresses [thanks Jim]
FIX: exception on repeatedly updating LOINC [thanks A.Maier]
FIX: exception on getattr() in braindead-tree-items-data-access workaround [thanks V.Banait]
FIX: exception on detecting patient ID column in patient listing ctrl [thanks Marc]

IMPROVED: show "U" for soapU data rather than "?" [thanks Jim]
IMPROVED: print recalls from vaccinations list

	18.6

FIX: clin_root_item_soap_cat check needs dropping
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.5');
