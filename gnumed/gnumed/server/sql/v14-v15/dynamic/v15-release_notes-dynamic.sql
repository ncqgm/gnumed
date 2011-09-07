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
	'Release Notes for GNUmed 0.9.10 (database v15.10)',
	'GNUmed 0.9.10 Release Notes:

	0.9.10

FIX: include latest GPL v2.0 license text from FSF [thanks Ankur]
FIX: gracefully handle invalid DOB (future, DOB > DOD) [thanks Wim]

IMPROVED: substance intake table: "amount per unit" = "Strength", not "Dose" [thanks J.Busser]

	15.10

FIX: cannot restore --single-transaction because CREATE DATABASE does not transact [thanks S.Reus]

IMPROVED: better commenting of informative messages in -roles.sql
');

-- --------------------------------------------------------------
