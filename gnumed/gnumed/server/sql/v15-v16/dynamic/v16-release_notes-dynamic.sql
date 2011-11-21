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
	'Release Notes for GNUmed 1.1.4 (database v16.4)',
	'GNUmed 1.1.4 Release Notes:

	1.1.4

FIX: document comment phrasewheel exception [thanks S.Reus]
FIX: exception in fuzzy timestamp PRW when not actively selecting from dropdown [thanks S.Reus]
FIX: exception in date input prw when not actively selecting from dropdown [thanks S.Reus]
FIX: exception on using "n" -> "now" in date input PRW
FIX: failure to properly propagate changes to the current encounter [thanks J.Busser]

IMPROVED: placeholder $<current_provider_external_id::type//issuer::length>$
IMPROVED: staff list editor: disable non-functional [Delete] button [thanks J.Busser]
IMPROVED: episode/issue EA: "Synopsis" field label/tooltip [thanks J.Busser]

	16.4

IMPROVED: make i18n._() check language "generic" before returning untranslated string
');

-- --------------------------------------------------------------
