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
	'Release Notes for GNUmed 1.7.7 (database v22.7)',
	'GNUmed 1.7.7 Release Notes:

	1.7.7

FIX: EMR/tree: exception on showing visual progress note
FIX: lab/result EA: exception when no previous result available
FIX: meds/substance EA: exception when no LOINC selected
FIX: data/ATC: fix reference data import
FIX: meds/dose EA: exception on saving
FIX: meds/product EA: exception on creating new product
FIX: dist: fix appdata.xml [thanks Andreas]

NEW: configurable invoice ID template [thanks Marc]

	22.7

IMPROVED: lab results plotting scripts for gnuplot
IMPROVED: bills tables grants for invoice ID generation

NEW: multi-results plotting script for gnuplot
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.7');
