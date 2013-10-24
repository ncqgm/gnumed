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
	'Release Notes for GNUmed 1.4.rc2 (database v19.rc2)',
	'GNUmed 1.4.rc2 Release Notes:

	1.4.rc2

NEW: generic search in lists
NEW: nested placeholders
NEW: placeholder $<current_meds_for_rx>$
NEW: list sorting by column header click [thanks J.Luszawski]
NEW: "Grünes Rezept" for Germany
NEW: manage your praxis with its branches
NEW: auto-hint "GVK-GU überfällig"
NEW: placeholder $<praxis>$
NEW: placeholder $<praxis_address>$
NEW: placeholder $<praxis_comm>$
NEW: dialog for post-processing template-generated documents
NEW: meta test type editing
NEW: management of billables
NEW: turn patient report results into waiting list entries
NEW: show relevant measurements in current substances list
NEW: AUDIT alcohol disorder screening
NEW: print/export of EMR timeline
NEW: ATRIA OAC bleeding risk score
NEW: export of individual document parts
NEW: EMR tree: support showing revisions
NEW: manual deletion of encounters

IMPROVED: hook nesting/cycling detection
IMPROVED: document in chart mailing of document parts
IMPROVED: just set DB lang at startup if missing, do not ask
IMPROVED: substance intake EA: PRW_aim context dependant on substance
IMPROVED: encounter EA: improved display of patient context
IMPROVED: new patient EA: warn on existing external ID
IMPROVED: new patient EA: warn on existing name + DOB
IMPROVED: substance PRW: prefer previously used as suggestions
IMPROVED: report failing auto-hints to the user
IMPROVED: make <Privacy notice> be category "admin" so they do not delete to soapU
IMPROVED: measurements workflow adjustments [thanks Jim and Rogerio]
IMPROVED: enable generic lists" extra buttons to operate on multi-selections
IMPROVED: access level role names
IMPROVED: check MD5 sum of newly inserted document objects for extra paranoia
IMPROVED: current medication list template
IMPROVED: backup/restore automatically applies DB settings adjustments
IMPROVED: default episode "administrative" rather than "administration"
IMPROVED: EMR tree: listing/editing switch button label
IMPROVED: EMR tree: show journal for unassociated episodes pool
IMPROVED: EMR tree: keep expansion state across node edits
IMPROVED: current_meds_tables/*_notes placeholder can now span pages
IMPROVED: waiting list [thanks Jerzy]
IMPROVED: streamlined form templates management
IMPROVED: display of long-text test results
IMPROVED: improved SOAP selection list
IMPROVED: more clinically relevant display of substance intake start
IMPROVED: test results plotting: deal with "<N" and ">N" pseudo-numeric values
IMPROVED: patient search now supports "LASTNAME, NICKNAME"
IMPROVED: document tree: keep expansion state across node edits

	19.rc2

Requires PostgreSQL 9.1 !

FIX: disable faulty clin-encounter.sql in v4 -> v5

NEW: view changes for Jerzy"s plugins
NEW: support data checksums with PG 9.3

IMPROVED: much simplified table mod announcement signal
IMPROVED: include FKs in schema version check
IMPROVED: remove .ddd/.unit from ref.atc
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.rc2');
