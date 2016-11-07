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
	'Release Notes for GNUmed 1.6.10 (database v21.10)',
	'GNUmed 1.6.10 Release Notes:

	1.6.10

FIX: more faults with dynamic hint detection
FIX: exception on verifying substance intake EA
FIX: failure to download studies from early Orthanc versions
FIX: failure to create BMP when no allergy check date available

IMPROVED: LaTeX formatting of current medications

NEW: placeholders $<bill_adr_*>$ for accessing the address of a bill
NEW: --wxp=2|3 command line option

	21.10

FIX: clin.get_hints_for_patient()
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.10');
