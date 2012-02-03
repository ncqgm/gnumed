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
	'Release Notes for GNUmed 1.1.11 (database v16.11)',
	'GNUmed 1.1.11 Release Notes:

	1.1.11

FIX: proper quoting of "start" args on Windows [thanks S.Hilbert]
FIX: exception on expando resizing when it holds 0 lines
FIX: exception on adding a second/third brand [thanks Vaibhav]

IMPROVED: remove unneeded documentation tarball [thanks A.Tille]
IMPROVED: better index.html in tarballed documentation [thanks A.Tille]
IMPROVED: ignore wx.Begin/EndBusyCursor refcounting
IMPROVED: PRWs now know about <ENTER> on Windows [thanks S.Hilbert]
IMPROVED: grey out arriba menu item if not detected [thanks S.Hilbert]
IMPROVED: pre-final editing of LaTeX forms [thanks M.Angermann]

	16.11

IMPROVED: add Russian DB string translations [thanks anon]
');

-- --------------------------------------------------------------
