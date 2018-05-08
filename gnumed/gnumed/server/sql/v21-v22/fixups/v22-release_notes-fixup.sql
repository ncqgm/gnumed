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
	'Release Notes for GNUmed 1.7.2 (database v22.2)',
	'GNUmed 1.7.2 Release Notes:

	1.7.2

FIX: GTK3 related size adjustments for PatientOverview/SimpleSoap plugins
FIX: GTK3 related bitmap adjustments
FIX: [Save] functionality of Export Area
FIX: placeholders $current_provider_[title/firstnames/lastnames]$
FIX: receiver selection address list setup

	1.7.1

NEW: add bash completion script

IMPROVED: make DWV optional
IMPROVED: prerequisites check tool
IMPROVED: update timeline code to 1.17.0 release

	22.2

FIX: staff/v_staff plausibility check [thanks Marc]
FIX: LaTeX-Template for Begleitbrief

	22.1

IMPROVED: concurrency robustness of backup/restore scripts
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.2');
