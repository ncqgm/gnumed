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
	'Release Notes for GNUmed 1.1.13 (database v16.13)',
	'GNUmed 1.1.13 Release Notes:

	1.1.13

FIX: apparent-age calculation bug on Feb 29th if DOB is non-leap year [thanks M.Angermann]
FIX: cFuzzyTimestampInput.is_valid_timestamp() error seen in encounter EA [thanks J.Busser]
FIX: Easter Egg Exception
FIX: [Save under] in SOAP editor would fail [thanks J.Busser]
');

-- --------------------------------------------------------------
