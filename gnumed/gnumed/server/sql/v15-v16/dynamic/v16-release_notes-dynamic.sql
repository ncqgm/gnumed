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
	'Release Notes for GNUmed 1.1.1 (database v16.1)',
	'GNUmed 1.1.1 Release Notes:

	1.1.1

FIX: more robust clock value formatting
FIX: when configured encounter type not available pick first rather than pk=0 one
FIX: failure to properly search for "kir;" [thanks J.Busser]
FIX: faulty use of wxSizer.Detach() [thanks Stepanyuk]

IMPROVED: log gmI18N.get_encoding() result
IMPROVED: encounter type phrasewheel formatting
IMPROVED: slightly better wx.EndBusyCursor() placement in exception handler
IMPROVED: formatting of staff match provider items [thanks J.Busser]
IMPROVED: by default show inactive substances in grid
IMPROVED: add improved icon XPM

	16.1

FIX: add back clin.v_narrative4search [thanks J.Busser]
FIX: remove stray ";" from org contact numbers report SQL [thanks J.Busser]

IMPROVED: do not log now-invalid RCS metadata anymore during bootstrapping
IMPROVED: docs for Debian''s pg_upgrade helper script
');

-- --------------------------------------------------------------
