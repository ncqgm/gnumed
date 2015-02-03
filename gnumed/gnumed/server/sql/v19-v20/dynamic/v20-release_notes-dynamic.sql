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
	'Release Notes for GNUmed 1.5.3 (database v20.3)',
	'GNUmed 1.5.3 Release Notes:

	1.5.3

FIX: HL7 import [thanks Jim]
FIX: VCF export with address/phone
FIX: LinuxMedNews XML export with address/phone
FIX: wx.HIDE_READONLY is no more
FIX: wxp2.8 does not yet have GetToolTipString()
FIX: creating dynamic hints [thanks Jim]
FIX: editing-from-encounter-list w/o encounter selected [thanks Jim]
FIX: properly LaTeX-escape "\n" into "\\" [thanks Jim]

IMPROVED: do not require simplejson in gmKVK
IMPROVED: show ext IDs/comm channels in EMR Journal Export
IMPROVED: provider inbox labels [thanks Jim]
IMPROVED: most recent test result display in patient overview [thanks Jim]
IMPROVED: select-day shows results in by-day test results panel [thanks Jim]
IMPROVED: $<gen_adr_*>$ can now cache several instances [thanks Jim]
IMPROVED: $<receiver_*>$ can now cache several instances [thanks Jim]

	20.3

FIX: setting FK to clin.test_org on dangling test types, really, this time
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-release_notes-dynamic.sql', '20.3');
