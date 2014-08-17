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
	'Release Notes for GNUmed 1.5.rc2 (database v20.rc2)',
	'GNUmed 1.5.rc2 Release Notes:

	1.5.rc2

NEW: by-day display mode for test results including multi-line ones
NEW: patient documents export area plugin
NEW: manage automatic dynamic hints
NEW: letter receiver placeholders $<receiver_*>$
NEW: EDC storage/calculator
NEW: external care documentation
NEW: print manager
NEW: external IDs on organizational units
NEW: better logging of SEGFAULT et alii
NEW: fully placeholdered general letter template
NEW: HL7 lab results import
NEW: Wells Score for pulmonary embolism

IMPROVED: filter inbox to active patient if called from waiting list [thanks Jim]
IMPROVED: robustness of patient change event sequence ordering
IMPROVED: import upstream TimeLine 1.2.3 release
IMPROVED: encounter editing before patient switch/creation
IMPROVED: manage episodes from measurements EA [thanks Jim]
IMPROVED: workflow when entering test result with new type
IMPROVED: updated to TimeLine 1.3.0 version
IMPROVED: on list updates scroll to last selected row if possible
IMPROVED: updated DVT Wells Score
IMPROVED: enhance dynamic keyword text expansions
IMPROVED: support test results status / source data
IMPROVED: link to WHO ATC list from drug/substance EA [thanks Jim]
IMPROVED: wxPython 3 compatibility

	20.rc2

IMPROVED: set clin.encounter.fk_location NOT NULL
IMPROVED: set clin.test_type.fk_test_org NOT NULL
IMPROVED: get rid of old-style schema notification
IMPROVED: database docs now per schema
IMRPOVED: auto-generation of episode/encounter FK sanity check triggers

NEW: clin.external_care
NEW: clin.patient
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-release_notes-dynamic.sql', '20.rc2');
