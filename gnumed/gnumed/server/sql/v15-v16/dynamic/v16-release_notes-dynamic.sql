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
	'Release Notes for GNUmed 1.1.3 (database v16.3)',
	'GNUmed 1.1.3 Release Notes:

	1.1.3

FIX: phrasewheel exception on test types without .code [thanks J.Busser]

	16.3

FIX: failure to create gm-staff group role when bootstrapping in a virgin PostgreSQL [thanks Debian]

IMPROVED: robustify GNUmed related PostgreSQL roles management
');

-- --------------------------------------------------------------
