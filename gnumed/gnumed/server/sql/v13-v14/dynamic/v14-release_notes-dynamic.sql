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
	'Release Notes for GNUmed 0.8.3 (database v14.3)',
	'GNUmed 0.8.3 Release Notes:

	0.8.3

FIX: missing gmHooks import when _on_soap_modified is invoked
FIX: exception due to faulty SQL in branded drug phrasewheel match provider
FIX: faulty German translation of (meningococcus) "A" to (meningococcus) "D"
FIX: subtle bug with validating date_deceased preventing demographics editing

	0.8.2

FIX: assertion on Windows when creating timestamps piecemeal in new-patient
FIX: exception on wrapping long entry in auto-expanding SOAP note field

	0.8.1

FIX: exception when "DejaVu Sans" not found on Windows
');

-- --------------------------------------------------------------
