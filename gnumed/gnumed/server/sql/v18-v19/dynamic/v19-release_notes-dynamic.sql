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
	'Release Notes for GNUmed 1.4.6 (database v19.6)',
	'GNUmed 1.4.6 Release Notes:

	1.4.6

FIX: missing qualification of make_pg_exception_fields_unicode() [thanks Khalil]
FIX: missing method in TimeLine code
FIX: bug in new-person EA validation code
FIX: creating dummy identities used faulty gender
FIX: faulty apparent_age formatting (age between 1-2 month ignored)
FIX: attempt to use "chart review" encounter type even if it does not exist [thanks Jim]

IMPROVED: DOB/age display in top panel
IMPROVED: deal with display of missing gender

	19.6 -- Requires PostgreSQL 9.1 !
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-release_notes-dynamic.sql', '19.rc2');
