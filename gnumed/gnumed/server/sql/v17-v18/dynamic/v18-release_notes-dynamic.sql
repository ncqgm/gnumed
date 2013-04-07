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
	'Release Notes for GNUmed 1.3.2 (database v18.2)',
	'GNUmed 1.3.2 Release Notes:

	1.3.2

FIX: failure to fully escape % in Xe(La)TeX engine [thanks V.Banait]
FIX: formatting error in current substance intake list
FIX: collision of placeholder replacement and text expansion filling
FIX: exception on substance-discontinued in the future [thanks S.Hilbert]
FIX: exception on months of different length in timeline [thanks S.Hilbert]
FIX: faulty use of test results formatting
FIX: intake EA forgot non-brand preparation [thanks S.Hilbert]
FIX: re-saving of durations when editing substance intakes [thanks S.Hilbert]
FIX: unable to save same-day hospital admission/discharge

IMPROVED: record deletion of inbox messages in EMR
IMPROVED: create recalls from vaccinations manager
IMPROVED: clean up LaTeX/Xe(La)TeX handling
IMPROVED: keep a copy of printed current medication lists [thanks Liz]
IMPROVED: add MELD score [thanks S.Hilbert]
IMPROVED: include duration with current_meds_table [thanks V.Banait]


	18.2

FIX: fake .due_/.expiry_date must be TIMESTAMP WITH TIME ZONE (not DATE)
FIX: faultily quoted DB translations/translation exporter
FIX: adjust dynamic text expansions to new HINT detection format

IMPROVED: French DB translations
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-release_notes-dynamic.sql', '18.2');
