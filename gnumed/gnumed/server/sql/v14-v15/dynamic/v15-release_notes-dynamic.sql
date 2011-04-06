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
	'Release Notes for GNUmed 0.9.1 (database v15.1)',
	'GNUmed 0.9.1 Release Notes:

Client

	0.9.1

FIX: wxPython-MSW (wx-assertions-on) cannot detach sizer items as documented [thanks S.Hilbert]
FIX: adjusted Python interpreter path in check-prerequisites.py [thanks lintian]
FIX: exception on calling FreeDiams on Windows if not configured [thanks S.Hilbert]

Database

	15.1

IMPROVED: upgrader now checks whether template database exists [thanks A.Tille]
IMPROVED: upgrader now fails when backup before upgrade fails [thanks A.Tille]

	15.0

NEW: script to fingerprint GNUmed databases
NEW: script to dump schema and roles for database debugging

IMPROVED: bootstrapper now detects commented out authentication directive [thanks Vid]

FIX: quoting in script to set gm-dbo password [thanks vbanait@gmail.com]
');

-- --------------------------------------------------------------
