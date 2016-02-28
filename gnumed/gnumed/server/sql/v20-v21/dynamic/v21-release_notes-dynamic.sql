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
	'Release Notes for GNUmed 1.6.0 (database v21.0)',
	'GNUmed 1.6.0 Release Notes:

	1.6.0

NEW: plugin: list based EMR journal
NEW: plugin: limited PACS access (Orthanc DICOM server)
NEW: text editor like SOAP editor (STC based)
NEW: first cut at German AMTS medication plan
NEW: always display select measurements in top panel
NEW: copy-to-clipboard list content via popup menu
NEW: region support for placeholder output
NEW: ellipsis support for placeholder output
NEW: placeholder $range_of$
NEW: placeholder $ph_cfg$
NEW: placeholder $current_meds_AMTS$
NEW: placeholder $praxis_vcf$
NEW: placeholder <form_version_internal>
NEW: placeholder <form_last_modified>
NEW: placeholder $url_escape$
NEW: add appdata.xml
NEW: show patient address in openstreetmap
NEW: support for substance abuse status (nicotine, ethanol, other)
NEW: print EMR from EMR tree
NEW: search in EMR journal view
NEW: copy EMR journal to export area
NEW: tooltip in procedures list
NEW: browse tmp dir, ~/gnumed/, ~/.gnumed/ from client
NEW: dynamic hint on outdated / questionable EDC
NEW: HIT risk assessment algorithm

IMPROVED: substance intake editing workflow
IMPROVED: shutdown with dangling top level windows
IMPROVED: list suppressed dynamic hints in patient overview [thanks Jim]
IMPROVED: top panel active encounter area layout [thanks Jim]
IMPROVED: measurements plots layout
IMPROVED: injectable placeholders: support arbitrary names if desired
IMPROVED: placeholder nesting regexen
IMPROVED: enable nested placeholders in text engine, too
IMPROVED: lab_panel.most_recent_results() can now respect meta types
IMPROVED: ignore_dupes_on_picking seems a better item picker default
IMPROVED: overall code towards Python 3 compatibility
IMPROVED: CODE: cIdentity(Tag) -> cPerson(Tag)
IMPROVED: security of tmp/sandbox dir setup
IMPROVED: do not auto-plot results from edit area
IMPROVED: much faster access to latest vaccinations
IMPROVED: show all selected parts at once in new-document plugin
IMPROVED: ask whether to create metadata when saving export area documents
IMPROVED: EMR journal formatting
IMPROVED: support deleting more than one list item at a time
IMPROVED: put file from filename in clipboard into export area
IMPROVED: startup shell script
IMPROVED: procedure tooltip in patient overview Hx box
IMPROVED: external care tooltip in patient overview problems box
IMPROVED: tooltip in external care management list
IMPROVED: substance intake timeframe formatting
IMPROVED: layout of measurements plugin
IMPROVED: properly show visual progress notes for empty issues in EMR tree
IMPROVED: support for invoking file manager on a directory
IMPROVED: show admin SOAP in EMR tree at encounter level
IMPROVED: ACEI/pregnancy dynamic hint
IMPROVED: data mining SQL now wants $<ID_ACTIVE_PATIENT>$ rather than $<ID_active_patient>$
IMPROVED: can now delete EDC
IMPROVED: support documenting which organization a document originated from
IMPROVED: workflow for disabling an identity
IMPROVED: EMR Journal formatting of hospital stays
IMPROVED: new-document workflow
IMPROVED: German referral letter
IMPROVED: include clinical reminders with EMR Journal

	21.0

NEW: require PG 9.2 because of pg_trigger_depth()
NEW: dem.v_basic_person -> dem.v_active_persons
NEW: prevent deletion of staff records that are in use
NEW: smoking support in clin.patient
NEW: constraints on audit trail to be in the past
NEW: check for track_commit_timestamp on PG > 9.5
NEW: chunked md5() for large objects

IMPROVED: database restore default configuration
IMPROVED: more resilient backups
IMPROVED: all input files now utf8 (io.open() Py3 preps)
IMPROVED: dem.state -> dem.region
IMPROVED: dem.region.id -> dem.region.pk
IMPROVED: dem.urb.id_state -> dem.urb.fk_region

FIX: pg_trgm placement and use
FIX: trigger on clin.procedure normalizing .is_ongoing
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.0');
