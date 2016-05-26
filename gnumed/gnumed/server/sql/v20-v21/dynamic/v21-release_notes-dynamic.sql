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
	'Release Notes for GNUmed 1.6.6 (database v21.6)',
	'GNUmed 1.6.6 Release Notes:

	1.6.6

FIX: error when running gm-import_incoming as root
FIX: failure to show entries with soap_cat=NULL in EMR list journal
FIX: copy-pasto "nicotine" -> "ethanol"

IMPROVED: clear metadata panel after importing new document
IMRPOVED: enable editing of document source org
IMPROVED: list context menu layout
IMPROVED: handling of Windows locale names like Hungarian_Hungary [thanks Attila]
IMPROVED: AppData file
IMRPOVED: OOo/LO/SO detection [thanks John]
IMRPOVED: tree display of documents

NEW: calculate distance of patient address to your praxis
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.6');
