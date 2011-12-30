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
	'Release Notes for GNUmed 1.1.8 (database v16.8)',
	'GNUmed 1.1.8 Release Notes:

	1.1.8

FIX: exception on accessing diagnostic certainty phrasewheel [thanks J.Busser]
FIX: cannot pack with pyInstaller due to pubsub v1 API [thanks S.Hilbert]

IMPROVED: try robustifying wx.lib.pubsub listener facing pyInstaller damage [thanks MM]
IMPROVED: make opening URLs work better with Python 2.6 [thanks MM]
IMPROVED: detection of connection loss
');

-- --------------------------------------------------------------
