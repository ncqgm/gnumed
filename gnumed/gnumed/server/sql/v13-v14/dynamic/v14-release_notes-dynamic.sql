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
	'Release Notes for GNUmed 0.8.8 (database v14.8)',
	'GNUmed 0.8.8/14.8 Release Notes:

	0.8.8

FIX: failure to show patient image if created in a month with a name containing non-ASCII characters
FIX: fix sorting of EMR tree dummy health issue node [thanks S.Hilbert]
FIX: no more getStrAllTopics() in newer wx.lib.pubsubs [thanks S.Hilbert]

	0.8.7

FIX: incompatible transport formatting of bytea between pre-9.0 libpq and 9.0+ PG server [thanks D.Varrazzo]
FIX: exception on adding a diagnostic org (path lab)
FIX: pointed everything in this branch to publicdb.gnumed.de
FIX: exception on pressing [As planned] in substance intake EA [thanks dj-marauder@web.de]

	0.8.6

FIX: strftime() cannot take unicode argument when refreshing waiting list [thanks JB]
FIX: constrain hospital stay PRW to current patient in procedure EA
FIX: faulty medically sound formatting of apparent age when between 1 and 2 years of age [thanks Wildfang]
FIX: insufficient check of start/end field value when editing encounter details [thanks S.Reus]

	0.8.5

FIX: PostgreSQL 9.0 does not need "regex_flavor" anymore
FIX: exception after adding patient to waiting list [thanks JB]
FIX: properly refresh encounter list after editing one [thanks JB]
FIX: rectify confusing message when deleting meds [thanks JB]
FIX: properly set PYTHONPATH [thanks Debian Squeeze and JB]

	0.8.4

FIX: exception on trying to create hospital stay w/o episode [thanks devm]
FIX: exception on calculate_apparent_age(start=March 31st, end=February): invalid day for month [thanks S.Reus]

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

---------------------------------------------------------------

	14.5 -> 14.6

FIX: quoting in script to set gm-dbo password [thanks vbanait@gmail.com]

	14.4 -> 14.5

FIX: no more regex_flavor in PostgreSQL 9.0 (gm-adjust_db_settings)
IMPROVED: gm-restore_database

	14.3 -> 14.4

FIX: bootstrapping: properly drop constraints on gm.notifying_tables during v9 -> v10

	14.2 -> 14.3

FIX: check for vaccination dupes looking at all patients rather than the relevant one only

	14.0 -> 14.1

NEW: auto-include fixups for missing array functionality on PG 8.3, needed for conversion to v14

');

-- --------------------------------------------------------------
