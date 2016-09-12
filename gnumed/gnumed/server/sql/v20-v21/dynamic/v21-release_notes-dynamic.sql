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
	'Release Notes for GNUmed 1.6.9 (database v21.9)',
	'GNUmed 1.6.9 Release Notes:

	1.6.8

FIX: faulty detection of dynamic hint applicability
FIX: exception on Orthanc port out of bounds
FIX: setting address from list in receiver selection widget
FIX: no EMR user interaction when updating active encounter display
FIX: faulty by-day measurements display after patient change

IMPROVED: start-end formatting of substance intake
IMPROVED: select unicode character from SOAP STC context menu
IMPROVED: edit test results by context menu from lists
IMPROVED: AMTS data file generation (v2 -> v2.3)
IMPROVED: color of focussed line in STC-based SOAP editor
IMPROVED: information in Hx box of patient overview plugin

NEW: placeholder $<if_not_empty>$
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.9');
