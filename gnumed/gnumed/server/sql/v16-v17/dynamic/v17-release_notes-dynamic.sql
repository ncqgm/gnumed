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
	'Release Notes for GNUmed 1.2.9 (database v17.9)',
	'GNUmed 1.2.9 Release Notes:

	1.2.9

FIX: protect against unexplained double-fill of provider inbox
FiX: protect against capitalize('') [thanks Slappinjohn]
FIX: protect against yet another silly SetItemPyData issue

IMPROVED: non-overdue recalls display in patient overview
IMPROVED: show comm channel comment in patient overview

	17.9

FIX: senior installations might have clin_narrative_soap_cat_check [thanks M.Angermann]
');

-- --------------------------------------------------------------
