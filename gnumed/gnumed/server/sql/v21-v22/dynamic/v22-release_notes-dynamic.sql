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
	'Release Notes for GNUmed 1.7.0 (database v22.0)',
	'GNUmed 1.7.0 Release Notes:

	1.7.0

NEW: link document to procedure
NEW: link document to hospital stay
NEW: support receiver on documents
NEW: support inactivity of external care entries
NEW: DICOM image preview in PACS plugin
NEW: placeholder <$current_provider_name$>
NEW: placeholder <$current_provider_title$>
NEW: placeholder <$current_provider_firstnames$>
NEW: placeholder <$current_provider_lastnames$>
NEW: placeholder $<diagnoses>$
NEW: switch substance intakes to drug components only
NEW: monitor test results relevant to intakes
NEW: add a database sanity check tool
NEW: add a EMR structure export tool
NEW: more options for putting formatted EMR into export area
NEW: measurements sorted by problem
NEW: verify DICOM data integrity in Orthanc server
NEW: clinical hint about missing LOINCs

IMPROVED: EMR journal layout/retrieval speed
IMPROVED: patient overview usability
IMPROVED: document tree details view
IMPROVED: LaTeX formatting of current medications (port from 1.6 branch)
IMPROVED: early-connect error decoding
IMPROVED: fairly-recent encounter continuation logic
IMPROGED: handling of empty-encounter cleanup
IMPROVED: non-blocking update check
IMPROVED: non-blocking file description retrieval
IMPROVED: patient merging
IMPROVED: email sending framework
IMPROVED: export area workflow
IMPROVED: test results usability
IMPROVED: vaccine/vaccination handling
IMPROVED: test panels now LOINC based
IMPROVED: patient media creation
IMPROVED: use new timeline upstream
IMPROVED: Spanish translation [thanks Uwe]
IMPROVED: long QT syndrome hyperlink updated
IMPROVED: age/DOB tooltip in top panel
IMPROVED: measurements: access related docs from list-by-day
IMPROVED: patient studies download from PACS
IMPROVED: provider inbox layout

	22.0

NEW: revalidate constraints during database upgrade
NEW: deprecate gm-backup_* in favor of gm-backup
NEW: deprecate gm-restore_* in favor of gm-restore

IMPROVED: staging._journal_without_suppressed_hints -> clin._v_emr_journal_without_suppressed_hints
IMPROVED: safer backup scripts
IMPROVED: do not fail clin.remove_old_empty_encounters() but return FALSE on <2 encounters
IMPROVED: substance abuse entries can have arbitrary .discontinued
IMPROVED: rework vaccine/vaccination tables/views
IMPROVED: turn unique identity assertion into deferred constraint trigger
IMPROVED: allow empty and comment lines in schema change file list definitions
IMPROVED: bootstrapper error logging
IMPROVED: revive pg_upgrade helper

FIX: constrain clin.clin_root_item.soap_cat CHECK to lower case
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-dynamic.sql', '22.0');
