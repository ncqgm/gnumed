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
	'Release Notes for GNUmed 1.3.3 (database v18.3)',
	'GNUmed 1.3.3 Release Notes:

	1.3.3

FIX: failure to use active patient on adding waiting list entry [thanks S.Hilbert]
FIX: failure to print in some Windows installations [thanks V.Banait]

IMPROVED: primitive HL7 formatting
IMPROVED: added recalls document template
IMRPOVED: check files for readability before printing
IMPROVED: sorta workaround infamous TreeCtrl.GetPyData() PyAssertion

	18.3

FIX: faulty bill.trf_prevent_empty_bills [thanks S.Urbanek]
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.2');
