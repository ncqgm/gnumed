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
	'Release Notes for GNUmed 1.3.4 (database v18.4)',
	'GNUmed 1.3.4 Release Notes:

	1.3.4

FIX: exception on DDE access to IE when printing
FIX: exception on timeline display problems
FIX: exception on logging cIdentity.export_tray [thanks J.Busser]
FIX: billing EA ignored encounter selection [thanks J.Busser]

IMPROVED: prepare for static placeholder depreciation
IMPROVED: verbosely format duration in $<current_meds_list>$ [thanks V.Banait]
IMPROVED: "Cave:" field not red when known to not have allergies
IMPROVED: several reports on medications taken by patients
IMPROVED: display of dynamic text expansion fill-in
IMPROVED: duplicates error message in drug brands EA [thanks V.Banait]
IMPROVED: also invoke text macros with <CTRL-ALT-T>

	18.4

FIX: missing constraint clin.encounter.started <= clin.encounter.last_affirmed
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.2');
