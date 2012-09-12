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
	'Release Notes for GNUmed 1.2.4 (database v17.4)',
	'GNUmed 1.2.4 Release Notes:

	1.2.4

FIX: prevent invoices from getting attached to the wrong patient [thanks M.Angermann]
FIX: robustify EMR tree against corner cases on patient change

IMPROVED: drug component PRW: show external ID of brand if known

	17.4

FIX: add report to find wrongly assigned invoices [thanks M.Angermann]
FIX: add trigger to prevent linking of invoices and bills of different patients
FIX: guard against all-zero fractions on consumable substance amounts [thanks J.Busser]
');

-- --------------------------------------------------------------
