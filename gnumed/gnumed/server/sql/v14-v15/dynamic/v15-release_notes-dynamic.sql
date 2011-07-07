-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
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
	'Release Notes for GNUmed 0.9.7 (database v15.7)',
	'GNUmed 0.9.7 Release Notes:

	0.9.7

FIX: exception on creating allergy entry from non-brand substance intake [thanks J.Busser]
FIX: exception on creating measurement type without LOINC [thanks J.Busser]
FIX: exception with displaying list item tooltips [thanks Marc]
FIX: faulty pt_BR translation ("issue name" -> "issue_name") [thanks Rogerio]
FIX: fix DOB to be dated back one day sometimes [thanks S.Reus]

IMPROVED: better protect against translation errors
');

-- --------------------------------------------------------------
