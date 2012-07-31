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
	'Release Notes for GNUmed 1.2.2 (database v17.2)',
	'GNUmed 1.2.2 Release Notes:

	1.2.2

IMPROVED: more frequent waiting list updates [thanks J.Busser]
IMRPOVED: release mail word-smithing
IMPROVED: disambiguate "problem IS health issue" in SOAP editor [thanks J.Busser]
IMPROVED: better listing of bills w/o items [thanks J.Busser]

FIX: tooltip of bills w/o items [thanks J.Busser]
FIX: failure to save .tex bill files
FIX: faulty encounter matcher SQL [thanks J.Busser]

	17.2

FIX: incorrect auditing setup of ref.billable [thanks J.Busser]

IMPROVED: prevent bills w/o items [thanks J.Busser]
IMPROVED: warn on upgrade if target DB exists [thanks V.Banait]
');

-- --------------------------------------------------------------
