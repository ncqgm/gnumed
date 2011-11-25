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
	'Release Notes for GNUmed 1.1.5 (database v16.5)',
	'GNUmed 1.1.5 Release Notes:

	1.1.5

FIX: properly review partless documents [thanks J.Busser]
FIX: exception in episode name selection PRW [thanks S.Reus]
FIX: improper validity check in encounter EA [thanks S.Reus]

IMPROVED: placeholder $<primary_praxis_provider_external_id::type//issuer::length>$
IMPROVED: robustify browsing URLs against external problems [thanks Sergio]

	16.5

FIX: inability to store document descriptions > 1/3 of a PG buffer page [thanks J.Busser]
');

-- --------------------------------------------------------------
