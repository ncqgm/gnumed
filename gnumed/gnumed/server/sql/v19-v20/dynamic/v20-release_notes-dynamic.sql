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
	'Release Notes for GNUmed 1.5.0 (database v20.0)',
	'GNUmed 1.5.0 Release Notes:

	1.5.0

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
NEW: algorithm for choosing an NSAR
NEW: bill related reports
NEW: $<external_care>$ placeholder
NEW: read German eGK/KVK/PKVK on Windows
NEW: per-patient suppression of dynamic hints
NEW: clipboard-based XML-formatted demographics exchange (I.Valdes, LinuxMedNews)
NEW: enable TLS on sending bug reports
NEW: sort substance intake by start date [thanks Jim]
NEW: save report generator results as CSV file
NEW: vCard import/export (I.Valdes, LinuxMedNews)
NEW: LQTS clinical probability score

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
IMPROVED: "Relevant" messages mode in provider inbox
IMPROVED: GFR calculations
IMPROVED: prevent deletion of messages not belonging to current provider
IMRPOVED: display of medication related lab monitoring
IMPROVED: exception logging enhancements
IMPROVED: workflow creating bill w/ respect to VAT [thanks Marc]
IMRPOVED: workflow finding unreviewed test results [thanks Jim]
IMPROVED: new-documents virtual inbox message

	20.0

IMPROVED: set clin.encounter.fk_location NOT NULL
IMPROVED: set clin.test_type.fk_test_org NOT NULL
IMPROVED: get rid of old-style schema notification
IMPROVED: database docs now per schema
IMRPOVED: auto-generation of episode/encounter FK sanity check triggers
IMPROVED: clin.test_type.conversion_unit -> *.reference_unit

NEW: clin.external_care
NEW: clin.patient
NEW: bootstrapper now REINDEXes after upgrade
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-release_notes-dynamic.sql', '20.0');
