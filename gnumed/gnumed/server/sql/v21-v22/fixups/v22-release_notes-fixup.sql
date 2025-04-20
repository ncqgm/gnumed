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
	'Release Notes for GNUmed 1.8.21 (database v22.31)',
	'GNUmed 1.8.21 Release Notes:

	1.8.21

FIX: startup: crash on fingerprinting v15+ servers [thanks gm-dbo]

	1.8.20

FIX: startup: crash on fingerprinting episodes in DB if gm-staff [thanks Maria]
FIX: patient search: gm-staff shall not ensure patient-ness [thanks Maria]

	22.31

FIX: crash on fingerprinting v15+ servers [thanks gm-dbo]

	22.30

FIX: unique constraint on identity+name with multiple names per identity [thanks Maria]
FIX: gm-staff permissions on dem.v_pat_addresses [thanks Maria]
FIX: gm-staff permissions on dem.v_message_inbox [thanks Maria]
FIX: permissions on org/unit tables/views
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-release_notes-fixup.sql', '22.31@1.8.21');
