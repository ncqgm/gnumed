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
	'Release Notes for GNUmed 1.5.4 (database v20.4)',
	'GNUmed 1.5.4 Release Notes:

	1.5.4

FIX: LaTeX output of $soap_for_encounter$ [thanks Jim]
FIX: streamline fairly-recent encounter activation
FIX: patient instantiation in episode management tooltips
FIX: street PRW exception on streets w/o postcode
FIX: exception on moving SOAP between encounters (1.4.15)
FIX: exception in staff list if there is staff with deleted DB account (1.4.16)

IMPROVED: default consultation report
IMPROVED: logging of unexpected encounter changes
IMPROVED: run pdflatex with -recorder so package "currfile" can be used

	20.4

no changes
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-release_notes-dynamic.sql', '20.4');
