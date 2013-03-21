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
	'Release Notes for GNUmed 1.3.1 (database v18.1)',
	'GNUmed 1.3.1 Release Notes:

	1.3.1

FIX: make gmHL7 import optional [thanks J.Luszawski/A.Tille]
FIX: exception on showing timeline [thanks S.Hilbert]
FIX: exception on searching across EMRs [thanks V.Banait]
FIX: exception on formatting external IDs in overview [thanks S.Hilbert]
FiX: exception on merging patients with same comm channel [thanks M.Angermann]

IMPROVED: have prerequisite check look for python-hl7 [thanks J.Luszawski]
IMPROVED: patient overview waiting list hint tooltip [thanks J.Busser]

	18.1

FIX: gm-doctors must be member of gm-public
FIX: exception dumping schema revision history of early DB versions [thanks Š.Laczi]

IMPROVED: bootstrapper now checks gm.schema_revision AND public.gm_schema_revision
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.1');
