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
	'Release Notes for GNUmed 1.0.rc1 (database v16.rc1)',
	'GNUmed 1.0.rc1 Release Notes:

	1.0.rc1

NEW: use os.startfile() for printing where available
NEW: PDF printing via Acrobat Reader/gsprint.exe/os.startfile/IEx/MacPreview
NEW: use dem.remove_person(integer) DB function from gm-remove_person.sh
NEW: add man pages for more server-side shell scripts
NEW: multi-phrase phrasewheel support
NEW: right-clicking problem in SOAP note plugin shows episode/issue edit area
NEW: cleanup tmp dir on shutdown if not running with --debug
NEW: do not import mx.DateTime in gmPG2.py anymore
NEW: LaTeX template for printing German "GKV-Rezept based" forms [thanks C.Becker]
NEW: hook "after_code_link_modified"
NEW: family history handling
NEW: PDF-form based forms handling via pdftk
NEW: coding of episodes, issues, RFE/AOE, procedures, family history
NEW: minimal management of communication channel types
NEW: support for data packs installable from within the client
NEW: warn on/inform about access to medical chart of staff member
NEW: add Ginkgo CADx to list of minimally supported DICOM viewers
NEW: placeholder $<encounter_list::format template::length>$ to access list of encounters
NEW: visual progress note creation directly from image capture device
NEW: 4 new visual progress note templates [thanks J.Busser]
NEW: implement explicitely creating episodes from EMR tree or menu
NEW: implement organizations management
NEW: placeholder $<patient_address::type//formatting template::length>$
NEW: placeholder $<adr_region::type::length>$
NEW: placeholder $<adr_country::type::length>$
NEW: placeholder $<patient_comm::type::length>$
NEW: placeholder $<external_id::type//issuer::length>$
NEW: placeholder $<primary_praxis_provider>$

IMPROVED: substance intake EA: one line with tooltip for components info field
IMPROVED: substance intake EA: field naming and title
IMPROVED: config file comments
IMPROVED: context menu titles
IMPROVED: allergy manager: close button, confirm button naming
IMPROVED: larger lower border in gnuplot templates so year gets displayed properly
IMPROVED: detection of external executables
IMPROVED: default medication list template layout
IMPROVED: make inbox listen to/reload on doc/doc-review/identity changes
IMPROVED: typos in patient search field [thanks J.Busser]
IMPROVED: check for both "lowriter" and "oowriter" when using OOo/LO [thanks Marc]
IMPROVED: set database options at bootstrap, only check at connection setup
IMPROVED: fix tab order in SOAP plugin [thanks S.Leibner]
IMPROVED: EMR tree: disable Journal/Synopsis selection for nodes where it does not apply
IMPROVED: clarified license to "GPL v2 or later"
IMPROVED: demographics tooltips: in-database emergency contact, in-praxis primary provider
IMPROVED: substance intake grid: show advice column
IMPROVED: document archive: configure UUID generation
IMPROVED: document archive: new review modes (only if not by responsible/only if none)
IMPROVED: comm channel type PRW: filter out match candidate dupes [thanks J.Busser]
IMPROVED: document tree: more informative node formatting
IMPROVED: prescription: auto-sign if the current provider is the intended reviewer for the patient
IMPROVED: vaccination list formatting on episodes/encounters
IMPROVED: faster generation of PDFs from LaTeX templates
IMPROVED: waiting list: multi-line comment and item-based list tooltip
IMPROVED: document metadata editing: no more always-on-top, safer parts moving [thanks J.Busser]
IMRROVED: waiting list: keep selection on item when moving it within the list [thanks J.Busser]
IMPROVED: inbox: goto-patient as default action if pk_patient is not NULL [thanks J.Busser]
IMPROVED: DOB related identity handling
IMPROVED: new patient EA: include in-praxis primary provider [thanks J.Busser]
IMPROVED: during connect check whether database was properly bootstrapped

	16.0.rc1

IMPROVED: backup script and config file comments [thanks J.Busser]
IMPROVED: restore script: properly set data file permissions [thanks S.Reus]
IMPROVED: restore script: use "-o pipefail" to detect complex pipe failures

NEW: clin.remove_old_empty_encounters()
NEW: dem.remove_person(integer)
');

-- --------------------------------------------------------------
