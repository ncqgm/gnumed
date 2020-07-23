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
	'Release Notes for GNUmed 1.8.3 (database v22.13)',
	'GNUmed 1.8.3 Release Notes:

	1.8.3

NEW: tool: fingerprint_db

IMPROVED: forms: log pdflatex version

FIX: meds: drug data source selection [thanks bganglia892]
FIX: meds: ADR URL configuration [thanks bganglia892]
FIX: vaccs: ADR URL configuration [thanks bganglia892]
FIX: tests: LOINC import fixup [thanks bganglia892]
FIX: db: whitespace in connection parameters [thanks kikiruz]
FIX: startup: startup without console fails [thanks Marc]
FIX: top panel: incorrect age-at-birthday display
FIX: i18n: locale activation

	22.13

IMPROVED: bootstrapper logging
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.13@1.8.3');
