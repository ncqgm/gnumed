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
	'Release Notes for GNUmed 0.9.5 (database v15.5)',
	'GNUmed 0.9.5 Release Notes:

	Client 0.9.5

FIX: exception on trying to use Wine version of GL/MMI under Windows [thanks S.Hilbert]
FIX: adjust default Windows path to FreeDiams executable [thanks S.Hilbert]
FIX: exception on trying to put patient on same drug twice [thanks J.Busser]
FIX: Windows can"t check hook script for -rw------- with os.stat() [thanks LuisCapriles]
FIX: exception on DOB input because .strptime() returns TZ naive dates [thanks J.Busser]
FIX: exceptions on entering large integers into DOB field

IMPROVED: logging of hook script permissions [thanks L.Capriles]

	Database 15.5

FIX: faulty quoting in database backup scripts using "su -c" [thanks Marc]
');

-- --------------------------------------------------------------
