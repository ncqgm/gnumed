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
	'Release Notes for GNUmed 1.6.8 (database v21.8)',
	'GNUmed 1.6.8 Release Notes:

	1.6.8

FIX: remove dynamic hint lacking evidence of clinical relevance
FIX: off-by-one calculation of substance intake end date
FIX: faulty use of $<gender_mapper>$ in Begleitbrief template
FIX: fix EMR access deadlock in encounter display widget [thanks Marc]
FIX: exception on non-ASCII VCF data
FIX: exception displaying birthday/age of patient w/ estimated DOB
FIX: list sorting by column header click

IMPROVED: document tree orgs sort mode tooltips
IMPROVED: file description shell script
IMPROVED: less in-your-face default list tooltip
IMPROVED: update AMTS Medikationsplan to 2.3
IMPROVED: log file placement
IMPROVED: form template EA information
IMPROVED: logging of EMR access locking
IMPROVED: EMR journal: show applicable dynamic hints
IMRPOVED: ES translation [thanks Uwe]
IMPROVED: show comm channels of org units in receiver selection
IMPROVED: show doc sources as receiver selection candidates
IMPROVED: letter receiver selection widget layout
IMPROVED: logging of patient change encounter editing

NEW: placeholder $ph_cfg::encoding::$
NEW: blanko AMTS Medikationsplan ~2.3
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-release_notes-dynamic.sql', '21.8');
