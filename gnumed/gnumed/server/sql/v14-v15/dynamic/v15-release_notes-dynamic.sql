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
	'Release Notes for GNUmed 0.9.rc1 (database v15.rc1)',
	'GNUmed 0.9.rc1 Release Notes:

	0.9.0

NEW: use much enhanced, file-based FreeDiams API
NEW: support primary provider on patients along with configurable fallback
NEW: support array of contextual FKs per inbox message
NEW: support dicomscope as DICOM viewer
NEW: support summary field on health issues and episodes
NEW: translate database strings from within client and contribute translations
NEW: simplistic coding systems browser
NEW: cloning of workplaces
NEW: hook "post_person_creation"
NEW: placeholder: "emr_journal::soap//%(narrative)s//255//tex::9999"
NEW: LaTeX template: chronological EMR journal
NEW: placeholder: "free_text::tex//<purpose>::9999"
NEW: LaTeX template: generic free-text medical statement (English and German)
NEW: full manual management of substances/drug components/branded drugs
NEW: implement our own date picker
NEW: implement searchable tags with image/name/comment on patients
NEW: Greek translation
NEW: log failed gm-dbo database access in database during restricted procedures
NEW: change gm-dbo password from client
NEW: implement leaving a message for oneself/other providers
NEW: Gulich Score on GABHS in sore throat
NEW: implement generic method for downloading data packs
NEW: placeholder: "soap_for_encounters::soap//<date format>::9999"

IMPROVED: link test results directly to requests for them
IMPROVED: much better EMR tree root node tooltip
IMPROVED: improved adding of vaccinations
IMPROVED: now listing episodes/health issues at time of creation in EMR journal
IMPROVED: Boesner score now has internationally usable name: "Marburg CHD score"
IMPROVED: much better integration of visual progress notes
IMPROVED: procedures now support a duration and an "ongoing" state
IMPROVED: adjust to modified API of MMI/Gelbe Liste
IMPROVED: master data management interface
IMPROVED: fix "Current Substance Intake" edit area usability glitches (schedule, substance, preparation)
IMPROVED: much saner "deletion of substance intake entry" workflow
IMPROVED: logically cleaner substance intake handling
IMPROVED: find gm-print_doc in git tree, too
IMPROVED: relax URL sanity checks since Web 2.0 confuses all but the most sophisticated browsers
IMPROVED: default server profile names in gnumed.conf example
IMPROVED: alpha-sort list of master data lists as per mailing list
IMPROVED: external patient sources now generically import external IDs/comm channels/addresses
IMPROVED: fix detection of existing patient when loading from external source
IMPROVED: workplace plugin configuration using item picker
IMPROVED: in phrasewheel support dynamic part of tooltip based on selected item data
IMPROVED: location PRW in procedure EA: re-use hospitals from hospital stays
IMPROVED: support arriba 2.2.2 and its new file-based API
IMPROVED: substance intake grid: display unapproved by default
IMPROVED: default temporary directory now /tmp/gnumed/gm-<unique ID>/ per GNUmed instance
IMPROVED: menu structure creation such that accelerator keys work more reliably
IMPROVED: EMR tree can now display selective chronological journal on issues and episodes
IMPROVED: existing translations
IMPROVED: make showing audit trail a restricted procedure
IMPROVED: enable exporting of in-database form template
IMPROVED: show RFE/AOE in "recent notes" display in SOAP plugin
IMPROVED: much saner workflow when creating allergy entry from substance intake
IMPROVED: configurably auto-open editors for all open, recently worked-on problems when activating a patient
IMPROVED: SOAP plugin: [Save under] saves notelet under selectable rather than current encounter
IMPROVED: enable moving documents between encounters, mainly useful for visual progress notes
');

-- --------------------------------------------------------------
