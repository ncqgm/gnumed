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
	'Release Notes for GNUmed 1.2.7 (database v17.7)',
	'GNUmed 1.2.7 Release Notes:

	1.2.7

FIX: faulty LaTeX escaping of "\" special character [thanks V.Banait]
FIX: failure to announce auto-picks from PRW dropdowns [thanks J.Busser]
FIX: sanity check item/data count in lists [thanks J.Busser]
FIX: possibly faulty tooltips in patient overview meds list
FIX: ignore exception on backing up log file inside exception handler
');

-- --------------------------------------------------------------
