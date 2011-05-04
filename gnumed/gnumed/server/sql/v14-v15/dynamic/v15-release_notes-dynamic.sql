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
	'Release Notes for GNUmed 0.9.4 (database v15.4)',
	'GNUmed 0.9.4 Release Notes:

	0.9.4

FIX: gm-remove_person.sh did not properly delete persons [thanks J.Busser]
FIX: enable running arriba w/o an active patient
FIX: cEpisode.get_narrative() ignored <soap_cats> argument
FIX: wrapper around Python"s deficient strftime() [thanks J.Jaarsveld]
FIX: exception on displaying date deceased if not null [thanks J.Busser]
FIX: exception on activating non-existant patient from inbox message [thanks Oliver]

IMPROVED: make creating/updating tags a restricted procedure [thanks Rogerio]
IMPROVED: slightly relax external app exit code check on Windows [thanks vbanait]
IMPROVED: placeholder "soap_for_encounters" now sorts by SOAP cat rank, then by date [thanks vbanait]
IMRPOVED: better remove SOAP-less encounters from consultation report output [thanks vbanait]
IMPROVED: do not try to sign results if none selected
');

-- --------------------------------------------------------------
