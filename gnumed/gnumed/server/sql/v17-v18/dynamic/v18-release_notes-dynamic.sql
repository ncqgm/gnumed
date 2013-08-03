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
	'Release Notes for GNUmed 1.3.8 (database v18.8)',
	'GNUmed 1.3.8 Release Notes:

	1.3.8

FIX: better show all relevant test results in review dialog [thanks Rogerio]
FIX: failure of <PRW>.SetData(None)
FIX: multi-use PRW edit font growth

IMPROVED: make timeline end 1 year after end of data
IMPROVED: es and pt_BR translations

	18.8

FIX: typo in clin.trf_notify_reviewer_of_review_change()
FIX: ensure FKs on .fk_encounter/.fk_episode on clin.clin_root_item children
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.5');
