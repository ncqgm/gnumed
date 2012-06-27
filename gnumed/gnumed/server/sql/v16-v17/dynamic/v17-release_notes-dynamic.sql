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
	'Release Notes for GNUmed 1.2.1 (database v17.1)',
	'GNUmed 1.2.1 Release Notes:

	1.2.1

IMPROVED: user experience with SimpleNotes plugin [thanks J.Busser]
IMPROVED: tell when there is no address for billing [thanks S.Hilbert]
IMPROVED: suggest current user as primary provider on new patients [thanks J.Busser]
IMPROVED: AutoHotKey script [thanks V.Banait]
IMPROVED: login dialog size [thanks J.Busser/L.Dodd]
IMPROVED: show stats cover period in Activity overview plugin sub panel [thanks J.Busser]
IMPROVED: soft-wrapping SimpleNotes and $<free_text>$ input [thanks J.Busser]

FIX: FreeDiams XML file API
FIX: exception activating disabled patient from waiting list [thanks B.Uhl]
FIX: exception on saving allergy without onset date [thanks J.Busser]
FIX: exception on editing comm channel w/o comment [thanks J.Busser]
FIX: exception on d-clicking top panel encounter field w/o active patient [thanks J.Busser]

	17.1

FIX: insufficient waiting time formatting [thanks J.Busser]
');

-- --------------------------------------------------------------
